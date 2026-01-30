#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易所语言QA引擎 v1.0
- 读取CSV文件，对目标语言列执行全量扫描
- 12项检测规则，零遗漏
- 输出问题清单CSV + 控制台摘要
- 支持批量修正 + 多轮验证

用法:
  python qa_engine.py scan --lang 越语 --files app.csv h5.csv web.csv agent.csv
  python qa_engine.py fix --lang 越语 --issues 越南语问题清单.csv --files app.csv h5.csv
  python qa_engine.py verify --lang 越语 --files app.csv h5.csv web.csv agent.csv
"""

import csv
import re
import sys
import os
import argparse
import json
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

# ============================================================
# 1. 中文检测
# ============================================================
RE_CHINESE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')

def has_chinese(text):
    return bool(RE_CHINESE.search(str(text)))

def extract_chinese(text):
    return RE_CHINESE.findall(str(text))

def chinese_ratio(text):
    if not text: return 0
    cn = len(RE_CHINESE.findall(str(text)))
    return cn / max(len(str(text)), 1)

# ============================================================
# 2. 全角→半角映射
# ============================================================
FULLWIDTH_MAP = {
    '，': ',', '！': '!', '？': '?', '：': ':', '；': ';',
    '（': '(', '）': ')', '【': '[', '】': ']',
    '\u201c': '"', '\u201d': '"',  # " "
    '\u2018': "'", '\u2019': "'",  # ' '
    '～': '~', '…': '...', '—': '-',
    '、': ',', '。': '.', '《': '<', '》': '>',
    '丨': '|',
}
RE_FULLWIDTH = re.compile('[' + re.escape(''.join(FULLWIDTH_MAP.keys())) + ']')

def replace_fullwidth(text):
    """替换全角标点为半角"""
    result = text
    for fw, hw in FULLWIDTH_MAP.items():
        result = result.replace(fw, hw)
    return result

def has_fullwidth(text):
    return bool(RE_FULLWIDTH.search(str(text)))

# ============================================================
# 3. Mojibake检测
# ============================================================
RE_MOJIBAKE = re.compile(r'Ã¡|Ã©|Ã³|â€|áº|á»|Ã¢|Ã´|Æ°|Ä')

def has_mojibake(text):
    return bool(RE_MOJIBAKE.search(str(text)))

# ============================================================
# 4. HTML标签检测
# ============================================================
def has_broken_html(text):
    t = str(text)
    # 检查未闭合的标签
    open_tags = re.findall(r'<([a-zA-Z]+)[^>]*(?<!/)>', t)
    close_tags = re.findall(r'</([a-zA-Z]+)>', t)
    # 自闭合标签不算
    self_closing = {'br', 'hr', 'img', 'input', 'meta', 'link'}
    open_filtered = [tag.lower() for tag in open_tags if tag.lower() not in self_closing]
    close_filtered = [tag.lower() for tag in close_tags]
    if len(open_filtered) != len(close_filtered):
        return True
    # 检查 <br 没有 > 的情况
    if re.search(r'<br(?!\s*>|/>|\s)', t):
        return True
    return False

# ============================================================
# 5. 术语表加载
# ============================================================
def load_terminology(terminology_file):
    """从术语表.md文件加载术语字典"""
    terms = {}  # {中文: 标准翻译}

    if not os.path.exists(terminology_file):
        print(f"[WARNING] 术语表文件不存在: {terminology_file}")
        return terms

    with open(terminology_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析markdown表格中的术语
    # 格式: | 序号 | 中文 | English | 标准越语 | 出现次数 |
    # 或者覆盖表格: | 中文 | 标准翻译 | ❌ 禁止用法 | 备注 |
    in_table = False
    for line in content.split('\n'):
        line = line.strip()
        if not line.startswith('|'):
            in_table = False
            continue

        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]  # 去掉空单元格

        if not cells:
            continue

        # 跳过表头分隔行
        if all(c.replace('-', '').replace(':', '') == '' for c in cells):
            in_table = True
            continue

        # 跳过表头行
        if '序号' in cells[0] or '中文' in cells[0] or '分类' in cells[0]:
            in_table = True
            continue

        if len(cells) >= 4:
            # 尝试解析: 序号 | 中文 | English | 标准越语 | 出现次数
            try:
                int(cells[0])  # 序号是数字
                zh = cells[1].strip()
                standard = cells[3].strip()
                if zh and standard:
                    terms[zh] = replace_fullwidth(standard)
            except (ValueError, IndexError):
                pass

    return terms

def load_override_terms(terminology_file):
    """加载龙老师覆盖术语（最高优先级）"""
    overrides = {}  # {中文: 标准翻译}
    forbidden = {}  # {禁止用法: (标准翻译, 对应中文)}

    if not os.path.exists(terminology_file):
        return overrides, forbidden

    with open(terminology_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析核心术语替换表
    # | 中文 | 标准翻译 | ❌ 禁止用法 | 备注 |
    in_override = False
    for line in content.split('\n'):
        if '核心术语替换表' in line:
            in_override = True
            continue
        if in_override and line.startswith('###') and '核心术语替换表' not in line:
            # 到了下一个section但不是替换表的子节
            if '语境判断规则' in line or '错误翻译黑名单' in line or '大小写规则' in line:
                in_override = False
                continue

        if not in_override:
            continue

        if not line.strip().startswith('|'):
            continue

        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]

        if not cells or len(cells) < 3:
            continue
        if cells[0] in ('中文', '---') or all(c.replace('-','') == '' for c in cells):
            continue

        zh = cells[0].strip()
        standard = cells[1].strip()

        if zh and standard and zh != '中文':
            overrides[zh] = standard

            # 解析禁止用法
            if len(cells) >= 3:
                forbidden_text = cells[2].strip()
                if forbidden_text and '❌' not in forbidden_text and '禁止' not in forbidden_text:
                    for fb in forbidden_text.split(','):
                        fb = fb.strip()
                        if fb:
                            forbidden[fb] = (standard, zh)

    # 解析错误翻译黑名单
    in_blacklist = False
    for line in content.split('\n'):
        if '错误翻译黑名单' in line:
            in_blacklist = True
            continue
        if in_blacklist and line.startswith('###'):
            in_blacklist = False
            continue

        if not in_blacklist:
            continue

        if not line.strip().startswith('|'):
            continue

        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]

        if not cells or len(cells) < 3:
            continue
        if cells[0] in ('错误翻译', '---') or all(c.replace('-','') == '' for c in cells):
            continue

        wrong = cells[0].strip()
        correct = cells[1].strip()
        zh = cells[2].strip() if len(cells) >= 3 else ''

        if wrong and correct and wrong != '错误翻译':
            forbidden[wrong] = (correct, zh)

    return overrides, forbidden

def load_fragment_map(terminology_file):
    """加载中文片段→越南语映射表"""
    fragments = {}

    if not os.path.exists(terminology_file):
        return fragments

    with open(terminology_file, 'r', encoding='utf-8') as f:
        content = f.read()

    in_fragment = False
    for line in content.split('\n'):
        if '中文残留片段' in line and '映射' in line:
            in_fragment = True
            continue
        if in_fragment and line.startswith('##') and '中文残留片段' not in line:
            in_fragment = False
            continue

        if not in_fragment:
            continue

        if not line.strip().startswith('|'):
            continue

        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]

        if not cells or len(cells) < 2:
            continue
        if cells[0] in ('中文片段', '---') or all(c.replace('-','') == '' for c in cells):
            continue

        zh_frag = cells[0].strip()
        vi_replace = cells[1].strip()

        if zh_frag and vi_replace and zh_frag != '中文片段':
            fragments[zh_frag] = vi_replace

    return fragments

# ============================================================
# 6. WRONG_TERM 禁止术语检测（需语境判断）
# ============================================================

# 禁止术语规则：(禁止词, 正确词, 语境条件)
# 语境条件是一个函数，接收source(中文)返回bool
WRONG_TERM_RULES = [
    # (pattern_in_target, replacement, context_check_fn)
    # === 无条件替换 ===
    ('Hợp đồng tương lai', 'Futures', lambda s: True),
    ('hợp đồng tương lai', 'Futures', lambda s: True),
    ('Hợp đồng Tương lai', 'Futures', lambda s: True),

    # 算力 → Hashrate（v3.0统一）
    ('sức mạnh băm', 'Hashrate', lambda s: True),
    ('Sức mạnh băm', 'Hashrate', lambda s: True),
    ('Quyền lực tính toán', 'Hashrate', lambda s: True),
    ('Sức mạnh tính toán', 'Hashrate', lambda s: True),
    ('sức mạnh tính toán', 'Hashrate', lambda s: True),

    ('Kết Thúc Sớm?', 'Có kết thúc trước thời hạn không?', lambda s: True),
    ('Chấm dứt cai nghiện', 'Rút tiền đã đóng', lambda s: True),
    ('Xác nhận rút quân', 'Xác nhận rút tiền', lambda s: True),
    ('dakika', 'phút', lambda s: True),

    # 币币交易（v3.0龙老师校对）
    ('Giao dịch bằng đồng xu', 'Giao dịch đồng coin', lambda s: True),

    # 联盟统一用 Liên minh（v3.0）
    ('Liên đoàn', 'Liên minh', lambda s: True),

    # AI统一（v3.0）
    ('Trí tuệ nhân tạo', 'AI', lambda s: True),
    ('trí tuệ nhân tạo', 'AI', lambda s: True),

    # 拼写错误修正（v3.0 + v3.2）
    ('Đại chỉ', 'Địa chỉ', lambda s: True),
    ('Marj gin', 'Margin', lambda s: True),

    # 折U → USDT（v3.0 + v3.1扩充）
    ('gấp U', 'USDT', lambda s: True),
    ('chiết khấu theo USDT', 'USDT', lambda s: any(kw in str(s) for kw in ['折U', '折合U', 'USDT'])),
    ('chiết khấu U', 'USDT', lambda s: any(kw in str(s) for kw in ['折U', '折合U', 'USDT'])),
    ('giảm giá ở USDT', 'USDT', lambda s: any(kw in str(s) for kw in ['折U', '折合U', 'USDT'])),

    # 返佣 → Hoàn phí（v3.1: Giảm giá用于返佣语境是错的）
    ('Giảm giá tích lũy tại chỗ', 'Hoàn phí Spot tích lũy',
     lambda s: any(kw in str(s) for kw in ['返佣', '佣金'])),
    ('Chấm giảm giá', 'Hoàn phí Spot',
     lambda s: any(kw in str(s) for kw in ['返佣', '佣金', '现货'])),
    ('Giảm giá tích lũy', 'Hoàn phí tích lũy',
     lambda s: any(kw in str(s) for kw in ['返佣', '佣金'])),
    ('Giảm giá Futures', 'Hoàn phí Futures',
     lambda s: any(kw in str(s) for kw in ['返佣', '佣金', '合约'])),
    ('Giảm giá (giảm giá ở USDT)', 'Hoàn phí (USDT)',
     lambda s: any(kw in str(s) for kw in ['返佣', '折U'])),
    ('Giảm giá', 'Hoàn phí',
     lambda s: any(kw in str(s) for kw in ['返佣', '佣金']) and '折' not in str(s)),

    # 合约账户 → Tài khoản Futures（v3.0）
    ('Tài khoản Hợp đồng Tương lai', 'Tài khoản Futures', lambda s: True),
    ('Tài khoản Hợp đồng', 'Tài khoản Futures',
     lambda s: any(kw in str(s) for kw in ['合约账户', '合约'])),

    # 合约佣金等 tương lai 残留
    ('Ủy ban tương lai', 'Hoa hồng Futures', lambda s: True),
    ('Tên tương lai', 'Tên Futures', lambda s: True),
    ('tương lai', 'Futures',
     lambda s: any(kw in str(s) for kw in ['合约', '期货'])),

    # 业务盈亏（v3.0）
    ('Lợi nhuận và lỗ của doanh nghiệp', 'Lãi lỗ kinh doanh', lambda s: True),

    # 充提数据（v3.0）
    ('Dữ liệu gửi và rút tiền', 'Dữ liệu nạp và rút tiền', lambda s: True),

    # Al（字母L）→ AI
    ('Chiến lược Al', 'Chiến lược AI', lambda s: True),
    (' Al ', ' AI ', lambda s: True),  # 独立的Al

    # === 语境依赖 ===
    # sao chép → Copy Trade（跟单语境）
    ('Sao chép giao dịch', 'Copy Trade',
     lambda s: any(kw in str(s) for kw in ['跟单', '带单', '复制交易', 'Copy Trade'])),
    ('sao chép giao dịch', 'Copy Trade',
     lambda s: any(kw in str(s) for kw in ['跟单', '带单', '复制交易', 'Copy Trade'])),
    ('Giao dịch sao chép', 'Copy Trade',
     lambda s: any(kw in str(s) for kw in ['跟单', '带单', '复制交易', 'Copy Trade'])),
    ('giao dịch sao chép', 'Copy Trade',
     lambda s: any(kw in str(s) for kw in ['跟单', '带单', '复制交易', 'Copy Trade'])),

    # Giao ngay → Spot（现货语境）
    ('Giao ngay', 'Spot',
     lambda s: any(kw in str(s) for kw in ['现货'])),
    ('giao ngay', 'Spot',
     lambda s: any(kw in str(s) for kw in ['现货'])),

    # Nhà giao dịch → Trader（非OTC）
    ('Nhà giao dịch', 'Trader',
     lambda s: any(kw in str(s) for kw in ['交易员', '交易达人', '带单']) and not any(kw in str(s) for kw in ['OTC', '商家'])),

    # rebate / hoa hồng ngược → Hoàn phí
    ('rebate', 'Hoàn phí',
     lambda s: any(kw in str(s) for kw in ['返佣', '反佣', '佣金'])),
    ('hoa hồng ngược', 'Hoàn phí', lambda s: True),

    # Đơn hàng → Lệnh（交易语境）
    ('Đơn hàng', 'Lệnh',
     lambda s: any(kw in str(s) for kw in ['委托', '下单', '挂单', '订单', '撤单', '限价', '市价'])
           and not any(kw in str(s) for kw in ['购买', '付款', 'OTC', '法币', '商家', '买币', '卖币', '充值', '提现'])),
    ('đơn hàng', 'lệnh',
     lambda s: any(kw in str(s) for kw in ['委托', '下单', '挂单', '订单', '撤单', '限价', '市价'])
           and not any(kw in str(s) for kw in ['购买', '付款', 'OTC', '法币', '商家', '买币', '卖币', '充值', '提现'])),

    # Giá thị trường → Giá Market
    ('Giá thị trường', 'Giá Market',
     lambda s: any(kw in str(s) for kw in ['市价'])),
    ('giá thị trường', 'Giá Market',
     lambda s: any(kw in str(s) for kw in ['市价'])),

    # Giá giới hạn → Giá Limit
    ('Giá giới hạn', 'Giá Limit',
     lambda s: any(kw in str(s) for kw in ['限价'])),
    ('giá giới hạn', 'Giá Limit',
     lambda s: any(kw in str(s) for kw in ['限价'])),

    # Mở cửa / Đóng cửa → Mở/Đóng vị thế（仓位语境）
    ('Mở cửa', 'Mở vị thế',
     lambda s: any(kw in str(s) for kw in ['开仓', '仓位', '持仓'])),
    ('Đóng cửa', 'Đóng vị thế',
     lambda s: any(kw in str(s) for kw in ['平仓', '仓位', '持仓'])),
]

def check_wrong_term(target, source):
    """检查禁止术语，返回 (has_issue, fixed_text, details)"""
    if not target:
        return False, target, ''

    fixed = str(target)
    issues = []

    for pattern, replacement, context_fn in WRONG_TERM_RULES:
        # 不区分大小写查找
        idx = fixed.lower().find(pattern.lower())
        if idx >= 0 and context_fn(source):
            # 注意 "hóa đơn" 中的 "đơn" 不替换
            if pattern.lower() in ('đơn hàng',):
                if 'hóa đơn' in fixed.lower():
                    continue
            # 用实际位置替换（保留原始大小写的pattern匹配段）
            actual = fixed[idx:idx+len(pattern)]
            fixed = fixed[:idx] + replacement + fixed[idx+len(pattern):]
            issues.append(f'{actual}→{replacement}')

    if issues:
        return True, fixed, '; '.join(issues)
    return False, target, ''

# ============================================================
# 7. 空白检测
# ============================================================
def fix_whitespace(text):
    t = str(text)
    t = t.strip()
    t = re.sub(r'  +', ' ', t)
    return t

def has_whitespace_issue(text):
    t = str(text)
    if t != t.strip():
        return True
    if '  ' in t:
        return True
    return False

# ============================================================
# 8. 大小写检测（越南语）
# ============================================================
VIET_TIME_UNITS = ['ngày', 'giờ', 'phút', 'giây', 'tuần', 'tháng', 'năm']
VIET_KEEP_LOWER = ['của', 'và', 'hoặc', 'trong', 'cho', 'với', 'từ', 'đến', 'là', 'có', 'không', 'được', 'để']

def check_capitalization(text):
    """检查越南语大小写规范，返回 (has_issue, fixed)"""
    if not text or len(str(text).strip()) == 0:
        return False, text

    t = str(text).strip()

    # 如果以数字、符号、特殊字符开头，跳过
    if not t[0].isalpha():
        return False, t

    # 句首应大写
    fixed = t
    if t[0].islower():
        # 检查是否是数字后的时间单位（这种情况不该进来，因为第一个字符是字母）
        # 检查是否是小写介词（单独出现时也应该大写）
        fixed = t[0].upper() + t[1:]

    if fixed != t:
        return True, fixed
    return False, t

# ============================================================
# 9. 核心扫描函数
# ============================================================
def scan_row(row, target_col, source_col, lang_key_col, terms, overrides, forbidden, fragments, source_file):
    """扫描单行，返回问题列表 [(priority, type, current, suggestion, detail)]"""
    issues = []

    target = str(row.get(target_col, '')).strip() if row.get(target_col) else ''
    source = str(row.get(source_col, '')).strip() if row.get(source_col) else ''
    lang_key = str(row.get(lang_key_col, '')).strip() if row.get(lang_key_col) else ''
    row_id = str(row.get('编号ID', '')).strip()

    # === P0: EMPTY ===
    if not target and source:
        issues.append(('P0', 'EMPTY', target, '', '目标语言为空'))
        return issues  # 短路

    # === P0: UNTRANSLATED_COPY ===
    if target == source and has_chinese(source):
        issues.append(('P0', 'UNTRANSLATED_COPY', target, '', '未翻译，原样复制'))
        return issues  # 短路

    # === P0: CONTAINS_CHINESE / CHINESE_FRAGMENT ===
    if has_chinese(source) and has_chinese(target):
        ratio = chinese_ratio(target)
        if ratio >= 0.5:
            # 大量中文 = CONTAINS_CHINESE
            issues.append(('P0', 'CONTAINS_CHINESE', target, '', f'中文占比{ratio:.0%}'))
        elif ratio > 0:
            # 少量中文片段
            cn_chars = extract_chinese(target)
            # 尝试用片段映射自动修复
            fixed = target
            fixed_any = False
            for frag, replacement in fragments.items():
                if frag in fixed:
                    fixed = fixed.replace(frag, replacement)
                    fixed_any = True

            if fixed_any and not has_chinese(fixed):
                issues.append(('P0', 'CHINESE_FRAGMENT', target, fixed,
                              f'中文片段已自动替换: {"".join(cn_chars)}'))
            else:
                remaining = extract_chinese(fixed) if fixed_any else cn_chars
                issues.append(('P0', 'CHINESE_FRAGMENT', target, fixed if fixed_any else '',
                              f'中文片段残留: {"".join(remaining)}'))

    # === P0: MOJIBAKE ===
    if has_mojibake(target):
        issues.append(('P0', 'MOJIBAKE', target, '', '编码损坏'))

    # 当前 target 用于后续检测（可能已被片段修复）
    working_target = target
    for issue in issues:
        if issue[1] == 'CHINESE_FRAGMENT' and issue[3]:
            working_target = issue[3]
            break

    # === P1: FULLWIDTH_PUNCTUATION ===
    if has_fullwidth(working_target):
        fixed = replace_fullwidth(working_target)
        issues.append(('P1', 'FULLWIDTH_PUNCTUATION', target, fixed, '全角标点'))
        working_target = fixed

    # === P1: WRONG_TERM ===
    has_wt, wt_fixed, wt_detail = check_wrong_term(working_target, source)
    if has_wt:
        issues.append(('P1', 'WRONG_TERM', target, wt_fixed, wt_detail))
        working_target = wt_fixed

    # === P1: TERMINOLOGY_MISMATCH ===
    # 1) 用lang_key精确匹配
    # 2) 用source短文本精确匹配
    matched_standard = None
    match_source = None

    # 先查覆盖表
    if lang_key in overrides:
        matched_standard = overrides[lang_key]
        match_source = lang_key
    elif source in overrides:
        matched_standard = overrides[source]
        match_source = source
    # 再查完整术语表
    elif lang_key in terms:
        matched_standard = terms[lang_key]
        match_source = lang_key
    elif len(source) <= 8 and source in terms:
        matched_standard = terms[source]
        match_source = source

    if matched_standard:
        matched_standard = replace_fullwidth(matched_standard)
        # 跳过：标准翻译本身包含禁止术语（WRONG_TERM会处理）
        standard_has_forbidden = False
        for pattern, replacement, ctx_fn in WRONG_TERM_RULES:
            if pattern.lower() in matched_standard.lower() and pattern.lower() != replacement.lower():
                standard_has_forbidden = True
                break
        # Normalize: strip + collapse whitespace + lowercase for comparison
        def _norm(s): return ' '.join(s.lower().split())
        if not standard_has_forbidden and _norm(working_target) != _norm(matched_standard) and _norm(target) != _norm(matched_standard):
            issues.append(('P1', 'TERMINOLOGY_MISMATCH', target, matched_standard,
                           f'{match_source}: 当前「{working_target}」应为「{matched_standard}」'))

    # === P2: WHITESPACE ===
    if has_whitespace_issue(working_target):
        fixed = fix_whitespace(working_target)
        if fixed != working_target:
            issues.append(('P2', 'WHITESPACE', target, fixed, '空白问题'))
            working_target = fixed

    # === P2: CAPITALIZATION ===
    cap_issue, cap_fixed = check_capitalization(working_target)
    if cap_issue:
        issues.append(('P2', 'CAPITALIZATION', target, cap_fixed, '大小写规范'))
        working_target = cap_fixed

    # === P2: BROKEN_HTML ===
    if has_broken_html(working_target):
        issues.append(('P2', 'BROKEN_HTML', target, '', 'HTML标签损坏'))

    # 合并修正：所有issue的建议修正统一为最终累积修正结果
    if issues and working_target != target:
        for i, issue in enumerate(issues):
            # TERMINOLOGY_MISMATCH 保留自己的标准翻译（精确匹配）
            if issue[1] == 'TERMINOLOGY_MISMATCH':
                continue
            # 其他类型统一用最终累积修正
            issues[i] = (issue[0], issue[1], issue[2], working_target, issue[4])

    return issues

# ============================================================
# 10. INCONSISTENCY检测（跨行）
# ============================================================
def check_inconsistency(all_rows, target_col, source_col, terms, overrides):
    """检查同一源文本多种翻译"""
    source_translations = defaultdict(lambda: defaultdict(list))  # {source: {target: [row_ids]}}

    for row in all_rows:
        source = str(row.get(source_col, '')).strip()
        target = str(row.get(target_col, '')).strip()
        row_id = str(row.get('编号ID', '')).strip()
        file_name = row.get('__source_file__', '')

        if source and target and has_chinese(source):
            source_translations[source][target].append((row_id, file_name))

    issues = []
    for source, translations in source_translations.items():
        if len(translations) > 1:
            # 确定标准翻译
            standard = overrides.get(source) or terms.get(source)
            if standard:
                standard = replace_fullwidth(standard)
                # 如果标准含禁止术语，放弃用术语表标准
                for pattern, replacement, ctx_fn in WRONG_TERM_RULES:
                    if pattern.lower() in standard.lower() and pattern.lower() != replacement.lower():
                        standard = None
                        break
            if not standard:
                # 取频率最高的
                standard = max(translations.keys(), key=lambda t: len(translations[t]))

            for target, locations in translations.items():
                if target.lower() != standard.lower() and target != standard:
                    for row_id, file_name in locations:
                        issues.append({
                            'row_id': row_id,
                            'file': file_name,
                            'priority': 'P1',
                            'type': 'INCONSISTENCY',
                            'source': source,
                            'current': target,
                            'suggestion': standard,
                            'detail': f'同源文本「{source}」有{len(translations)}种翻译，应统一为「{standard}」'
                        })

    return issues

# ============================================================
# 11. 主扫描流程
# ============================================================
def get_file_label(filepath):
    """从文件名推断来源标签"""
    name = os.path.basename(filepath).lower()
    if 'app' in name: return 'APP'
    if 'h5' in name: return 'H5'
    if 'web' in name: return 'Web'
    if '代理' in name or 'agent' in name: return '代理后台'
    return os.path.basename(filepath)

def read_csv_file(filepath):
    """读取CSV文件"""
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            row['__source_file__'] = filepath
            rows.append(row)
    return rows, fieldnames

def run_scan(files, target_col, source_col, lang_key_col, terminology_file, output_dir):
    """执行全量扫描"""
    print(f"\n{'='*50}")
    print(f"交易所语言QA引擎 - 全量扫描")
    print(f"{'='*50}")
    print(f"目标语言列: {target_col}")
    print(f"源语言列: {source_col}")
    print(f"术语表: {terminology_file}")
    print(f"文件数: {len(files)}")
    print(f"{'='*50}\n")

    # 加载术语
    terms = load_terminology(terminology_file)
    overrides, forbidden = load_override_terms(terminology_file)
    fragments = load_fragment_map(terminology_file)

    print(f"术语表加载完成: {len(terms)} 条术语, {len(overrides)} 条覆盖, {len(forbidden)} 条禁止, {len(fragments)} 条片段映射")

    # 读取所有文件
    all_rows = []
    file_row_counts = {}

    for filepath in files:
        rows, fieldnames = read_csv_file(filepath)

        # 验证列名
        if target_col not in fieldnames:
            print(f"[ERROR] 文件 {filepath} 中未找到列 '{target_col}'")
            print(f"  可用列: {fieldnames}")
            continue
        if source_col not in fieldnames:
            print(f"[ERROR] 文件 {filepath} 中未找到列 '{source_col}'")
            continue

        file_row_counts[filepath] = len(rows)
        all_rows.extend(rows)
        print(f"  已读取: {filepath} ({len(rows)} 行)")

    print(f"\n总计: {len(all_rows)} 行\n")

    # 逐行扫描
    all_issues = []
    issue_counter = Counter()
    priority_counter = Counter()
    file_counter = Counter()

    for row in all_rows:
        filepath = row['__source_file__']
        file_label = get_file_label(filepath)
        row_id = str(row.get('编号ID', '')).strip()
        lang_key = str(row.get(lang_key_col, '')).strip() if lang_key_col and row.get(lang_key_col) else ''
        source = str(row.get(source_col, '')).strip()

        row_issues = scan_row(row, target_col, source_col, lang_key_col,
                             terms, overrides, forbidden, fragments, filepath)

        for priority, issue_type, current, suggestion, detail in row_issues:
            all_issues.append({
                'file': file_label,
                'filepath': filepath,
                'row_id': row_id,
                'priority': priority,
                'type': issue_type,
                'lang_key': lang_key,
                'current': current,
                'suggestion': suggestion,
                'detail': detail,
            })
            issue_counter[issue_type] += 1
            priority_counter[priority] += 1
            file_counter[file_label] += 1

    # INCONSISTENCY检测
    inconsistency_issues = check_inconsistency(all_rows, target_col, source_col, terms, overrides)
    for issue in inconsistency_issues:
        all_issues.append({
            'file': get_file_label(issue['file']),
            'filepath': issue['file'],
            'row_id': issue['row_id'],
            'priority': issue['priority'],
            'type': issue['type'],
            'lang_key': issue['source'],
            'current': issue['current'],
            'suggestion': issue['suggestion'],
            'detail': issue['detail'],
        })
        issue_counter['INCONSISTENCY'] += 1
        priority_counter['P1'] += 1
        file_counter[get_file_label(issue['file'])] += 1

    # 排序：P0 > P1 > P2，来源，编号ID降序
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
    file_order = {'APP': 0, 'H5': 1, 'Web': 2, '代理后台': 3}

    all_issues.sort(key=lambda x: (
        priority_order.get(x['priority'], 9),
        file_order.get(x['file'], 9),
        -int(x['row_id']) if x['row_id'].isdigit() else 0
    ))

    # 输出问题清单CSV
    output_file = os.path.join(output_dir, f'{target_col}问题清单.csv')
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['序号', '来源', '编号ID', '优先级', '问题类型', '语言标识', '当前翻译', '建议修正', '确认', '人工修正'])

        for i, issue in enumerate(all_issues, 1):
            writer.writerow([
                i,
                issue['file'],
                issue['row_id'],
                issue['priority'],
                issue['type'],
                issue['lang_key'],
                issue['current'],
                issue['suggestion'],
                '',
                ''
            ])

    # 控制台摘要
    print(f"\n{'='*50}")
    print(f"扫描摘要")
    print(f"{'='*50}")
    print(f"总问题数: {len(all_issues)}")
    print(f"\n按优先级:")
    for p in ['P0', 'P1', 'P2']:
        print(f"  {p}: {priority_counter[p]}")
    print(f"\n按问题类型:")
    for t in ['EMPTY', 'UNTRANSLATED_COPY', 'CONTAINS_CHINESE', 'CHINESE_FRAGMENT',
              'MOJIBAKE', 'FULLWIDTH_PUNCTUATION', 'WRONG_TERM', 'TERMINOLOGY_MISMATCH',
              'INCONSISTENCY', 'INCOMPLETE_TRANSLATION', 'WHITESPACE', 'CAPITALIZATION', 'BROKEN_HTML']:
        if issue_counter[t] > 0:
            print(f"  {t}: {issue_counter[t]}")
    print(f"\n按来源:")
    for src in ['APP', 'H5', 'Web', '代理后台']:
        if file_counter[src] > 0:
            print(f"  {src}: {file_counter[src]}")
    for src in file_counter:
        if src not in ('APP', 'H5', 'Web', '代理后台'):
            print(f"  {src}: {file_counter[src]}")
    print(f"\n问题清单已输出: {output_file}")
    print(f"{'='*50}\n")

    return all_issues, output_file

# ============================================================
# 12. 批量修正
# ============================================================
def run_fix(files, target_col, issues_file):
    """根据问题清单批量修正CSV"""
    print(f"\n{'='*50}")
    print(f"批量修正")
    print(f"{'='*50}\n")

    # 读取问题清单
    # 同一行多条记录时，取最长的suggestion（完整句优先于单一术语）
    fix_map = {}  # {(file_label, row_id): suggestion}
    with open(issues_file, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            suggestion = row.get('人工修正', '').strip() or row.get('建议修正', '').strip()
            if suggestion:
                key = (row['来源'], row['编号ID'])
                if key not in fix_map or len(suggestion) > len(fix_map[key]):
                    fix_map[key] = suggestion

    print(f"修正映射: {len(fix_map)} 条\n")

    for filepath in files:
        file_label = get_file_label(filepath)

        # 创建备份
        backup_path = filepath.replace('.csv', '_backup_原始.csv')
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(filepath, backup_path)
            print(f"  备份: {backup_path}")

        # 读取并修正
        rows, fieldnames = read_csv_file(filepath)
        modified = 0
        skipped = 0

        output_rows = []
        for row in rows:
            row_id = str(row.get('编号ID', '')).strip()
            key = (file_label, row_id)

            if key in fix_map:
                row[target_col] = replace_fullwidth(fix_map[key])
                modified += 1
            else:
                # 即使不在fix_map中，也清理全角标点
                val = row.get(target_col, '')
                cleaned = replace_fullwidth(val)
                if cleaned != val:
                    row[target_col] = cleaned
                    modified += 1
                else:
                    skipped += 1

            # 移除内部标记
            clean_row = {k: v for k, v in row.items() if k != '__source_file__'}
            output_rows.append(clean_row)

        # 写回
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for row in output_rows:
                writer.writerow(row)

        print(f"  {filepath}: {modified} 修改, {skipped} 跳过 (共 {len(rows)} 行)")

    print(f"\n修正完成")
    print(f"{'='*50}\n")

# ============================================================
# 13. 验证
# ============================================================
def run_verify(files, target_col, source_col, lang_key_col, terminology_file, output_dir):
    """修正后验证"""
    print(f"\n{'='*50}")
    print(f"验证")
    print(f"{'='*50}\n")

    # 列完整性验证
    all_pass = True

    for filepath in files:
        backup_path = filepath.replace('.csv', '_backup_原始.csv')
        file_label = get_file_label(filepath)

        if not os.path.exists(backup_path):
            print(f"  [SKIP] {file_label}: 无备份文件")
            continue

        # V1: 行数
        rows_new, fn_new = read_csv_file(filepath)
        rows_old, fn_old = read_csv_file(backup_path)

        v1 = len(rows_new) == len(rows_old)
        v2 = len(fn_new) == len(fn_old)

        # V3: 非目标列一致性（抽样20行）
        v3 = True
        sample_size = min(20, len(rows_new))
        import random
        sample_indices = random.sample(range(len(rows_new)), sample_size) if len(rows_new) > 20 else range(len(rows_new))

        for idx in sample_indices:
            for col in fn_new:
                if col == target_col or col == '__source_file__':
                    continue
                old_val = str(rows_old[idx].get(col, ''))
                new_val = str(rows_new[idx].get(col, ''))
                if old_val != new_val:
                    v3 = False
                    print(f"  [FAIL] V3: {file_label} 行{idx} 列'{col}' 被修改!")
                    break

        # V4: 编号ID完整性
        v4 = True
        for idx in range(min(len(rows_new), len(rows_old))):
            if rows_new[idx].get('编号ID') != rows_old[idx].get('编号ID'):
                v4 = False
                break

        status = "PASS" if (v1 and v2 and v3 and v4) else "FAIL"
        if status == "FAIL":
            all_pass = False

        print(f"  {file_label}:")
        print(f"    V1 行数: {'PASS' if v1 else 'FAIL'} ({len(rows_new)} vs {len(rows_old)})")
        print(f"    V2 列数: {'PASS' if v2 else 'FAIL'} ({len(fn_new)} vs {len(fn_old)})")
        print(f"    V3 非目标列: {'PASS' if v3 else 'FAIL'}")
        print(f"    V4 编号ID: {'PASS' if v4 else 'FAIL'}")

    # 重新扫描
    print(f"\n重新扫描...")
    issues, _ = run_scan(files, target_col, source_col, lang_key_col, terminology_file, output_dir)

    # 门禁检查
    p0_count = sum(1 for i in issues if i['priority'] == 'P0')
    fw_count = sum(1 for i in issues if i['type'] == 'FULLWIDTH_PUNCTUATION')
    cn_count = sum(1 for i in issues if i['type'] in ('CONTAINS_CHINESE', 'CHINESE_FRAGMENT'))
    mb_count = sum(1 for i in issues if i['type'] == 'MOJIBAKE')
    tm_count = sum(1 for i in issues if i['type'] == 'TERMINOLOGY_MISMATCH')

    gates = [
        ('Gate 1', '零致命问题', p0_count == 0, f'{p0_count} 条'),
        ('Gate 2', '零全角标点', fw_count == 0, f'{fw_count} 条'),
        ('Gate 3', '零中文残留', cn_count == 0, f'{cn_count} 条'),
        ('Gate 4', '零编码损坏', mb_count == 0, f'{mb_count} 条'),
        ('Gate 5', '术语一致性', tm_count == 0, f'{tm_count} 不匹配'),
        ('Gate 6', '行列不变', all_pass, '已验证' if all_pass else 'FAIL'),
    ]

    print(f"\n{'='*50}")
    print(f"验证报告")
    print(f"{'='*50}")

    all_gates_pass = all(g[2] for g in gates)

    for gate, name, passed, detail in gates:
        status = 'PASS' if passed else 'FAIL'
        print(f"  {gate} {name}: {status} ({detail})")

    verdict = "SAFE TO DEPLOY" if all_gates_pass else "NOT SAFE TO DEPLOY"
    print(f"\nVERDICT: {verdict}")
    print(f"{'='*50}\n")

    return all_gates_pass

# ============================================================
# 14. CLI入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='交易所语言QA引擎')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # scan
    scan_parser = subparsers.add_parser('scan', help='全量扫描')
    scan_parser.add_argument('--lang', required=True, help='目标语言列名（如"越语"）')
    scan_parser.add_argument('--source', default='简体中文', help='源语言列名（默认"简体中文"）')
    scan_parser.add_argument('--lang-key', default='语言标识', help='语言标识列名')
    scan_parser.add_argument('--terms', help='术语表文件路径（默认自动查找）')
    scan_parser.add_argument('--output', default='.', help='输出目录')
    scan_parser.add_argument('--files', nargs='+', required=True, help='CSV文件列表')

    # fix
    fix_parser = subparsers.add_parser('fix', help='批量修正')
    fix_parser.add_argument('--lang', required=True, help='目标语言列名')
    fix_parser.add_argument('--issues', required=True, help='问题清单CSV文件')
    fix_parser.add_argument('--files', nargs='+', required=True, help='CSV文件列表')

    # verify
    verify_parser = subparsers.add_parser('verify', help='验证')
    verify_parser.add_argument('--lang', required=True, help='目标语言列名')
    verify_parser.add_argument('--source', default='简体中文', help='源语言列名')
    verify_parser.add_argument('--lang-key', default='语言标识', help='语言标识列名')
    verify_parser.add_argument('--terms', help='术语表文件路径')
    verify_parser.add_argument('--output', default='.', help='输出目录')
    verify_parser.add_argument('--files', nargs='+', required=True, help='CSV文件列表')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 自动查找术语表
    SKILL_DIR = os.path.expanduser('~/.claude/skills/交易所语言QA')

    if args.command in ('scan', 'verify'):
        terms_file = args.terms
        if not terms_file:
            # 根据列名猜测语言
            lang_map = {'越语': '越南语', '韩语': '韩语', '日语': '日语', '英语': '英语', '泰语': '泰语'}
            lang_name = lang_map.get(args.lang, args.lang)
            terms_file = os.path.join(SKILL_DIR, '术语表', f'{lang_name}.md')

        if args.command == 'scan':
            run_scan(args.files, args.lang, args.source, args.lang_key, terms_file, args.output)
        else:
            run_verify(args.files, args.lang, args.source, args.lang_key, terms_file, args.output)

    elif args.command == 'fix':
        run_fix(args.files, args.lang, args.issues)

if __name__ == '__main__':
    main()
