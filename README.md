# NIVEX Skills 共享库

团队共享的 Claude Code Skills，一键安装到本地。

## 安装

```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash
```

> 前提：已安装 `gh` 并登录（`gh auth login`）

## 包含的 Skills

| Skill | 触发词 | 说明 |
|-------|--------|------|
| NIVEX_PPT | 做PPT、生成PPT | HTML演示文稿生成器 |
| AK_投资顾问 | AK、投资顾问 | 客户服务与销售支持 |
| 小玲翻译 | 小玲翻译、翻译一下 | 中越双语翻译 |
| 芳草_翻译助理 | 芳草翻译 | 翻译助理 |
| 交易所语言QA | 语言QA、翻译审查 | 多语言翻译质量审查 |
| 市场速递 | 市场速递、日报 | 每日行情分析 |
| 业务工作流 | 做工作流、流程拆解 | 目标倒推工作流生成 |
| 员工Skill评分 | Skill评分 | 员工能力评估 |

## 贡献新 Skill

1. Fork 仓库
2. 在 `skills/` 下创建新文件夹，包含 `SKILL.md`
3. 提交 PR，管理员审核后合并
