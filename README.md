# NIVEX Skills 共享库 / Thư viện Skills NIVEX

公司团队共用的 Claude Code Skills，按岗位分类，按需安装。
Thư viện Claude Code Skills dùng chung cho toàn đội, phân loại theo vị trí, cài đặt theo nhu cầu.

---

## 🚀 安装 / Cài đặt

打开 Claude Code 桌面版的终端，复制粘贴即可。
Mở terminal trong Claude Code Desktop, copy-paste là xong.

### 查看有哪些 Skills / Xem có những Skills nào
```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- --list
```

### 安装全部 / Cài tất cả
```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash
```

### 只装你需要的 / Chỉ cài cái bạn cần
```bash
# 例 / Ví dụ: 只装翻译和PPT
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 小玲翻译 NIVEX_PPT
```

---

## 📋 Skills 分类 / Phân loại theo vị trí

### 🎯 销售 & 客服 / Kinh doanh & CSKH

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả |
|-------|----------------------|-------------|
| `AK_投资顾问` | AK、投资顾问 | 客户咨询、异议处理、分类跟进 — Tư vấn KH, xử lý phản đối, phân loại & theo dõi |

```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- AK_投资顾问
```

---

### 🌐 翻译 & 语言 / Phiên dịch & Ngôn ngữ

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả |
|-------|----------------------|-------------|
| `小玲翻译` | 小玲翻译、翻译一下 | 中越双语翻译 — Dịch Trung-Việt, chú trọng ngữ khí |
| `芳草_翻译助理` | 芳草翻译 | 会议纪要、文档翻译 — Biên bản họp, dịch tài liệu |
| `交易所语言QA` | 语言QA、翻译审查 | 多语言翻译质量审查 — Kiểm tra chất lượng dịch đa ngôn ngữ |

```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 小玲翻译 芳草_翻译助理 交易所语言QA
```

---

### 📊 市场 & 运营 / Marketing & Vận hành

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả |
|-------|----------------------|-------------|
| `市场速递` | 市场速递、日报 | 每日 BTC/ETH 行情分析 — Phân tích BTC/ETH hàng ngày |
| `NIVEX_PPT` | 做PPT、生成PPT | HTML 演示文稿生成 — Tạo slide HTML |

```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 市场速递 NIVEX_PPT
```

---

### 🏢 管理 / Quản lý

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả |
|-------|----------------------|-------------|
| `业务工作流` | 做工作流、流程拆解 | 目标倒推工作流 — Quy trình đảo ngược từ mục tiêu |
| `员工Skill评分` | Skill评分 | 员工能力评估 — Đánh giá năng lực nhân viên |

```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 业务工作流 员工Skill评分
```

---

## 🔧 安装后怎么用 / Cài xong dùng thế nào

打开 Claude Code，直接说触发词：
Mở Claude Code, nói từ kích hoạt:

```
> 小玲翻译，帮我翻译一下这段话
> 做个PPT，主题是交易所介绍
> AK，这个客户问安全性怎么回答
> 市场速递
```

---

## 🔄 更新 / Cập nhật

重新运行安装命令即可，自动覆盖旧版。
Chạy lại lệnh cài đặt, tự động ghi đè phiên bản cũ.

---

## 🤝 贡献新 Skill / Đóng góp Skill mới

1. **Fork** 仓库 / Fork repo
2. 在 `skills/` 下建文件夹，放入 `SKILL.md` / Tạo thư mục trong `skills/`, thêm `SKILL.md`
3. 提 **Pull Request** / Gửi **Pull Request**

---

## ❓ 常见问题 / FAQ

**Q: 安装后没效果？/ Cài xong không thấy?**
> 重启 Claude Code。/ Khởi động lại Claude Code.

**Q: 怎么更新？/ Cập nhật thế nào?**
> 重新跑安装命令。/ Chạy lại lệnh cài đặt.

**Q: 不会用终端？/ Không biết dùng terminal?**
> 在 Claude Code 里直接对话说"帮我安装 NIVEX Skills"，它会引导你。
> Nói với Claude Code: "Giúp tôi cài NIVEX Skills", nó sẽ hướng dẫn bạn.
