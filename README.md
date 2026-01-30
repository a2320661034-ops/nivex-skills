# NIVEX Skills 共享库 / Thư viện Skills NIVEX

公司团队共用的 Claude Code Skills，按岗位分类，按需安装。
Thư viện Claude Code Skills dùng chung cho toàn đội, phân loại theo vị trí, cài đặt theo nhu cầu.

---

## 📥 安装前准备 / Chuẩn bị trước khi cài

### 1. 安装 Claude Code / Cài Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 安装 GitHub CLI / Cài GitHub CLI
```bash
# Mac
brew install gh

# Windows
winget install GitHub.cli
```

### 3. 登录 GitHub / Đăng nhập GitHub
```bash
gh auth login
```
> 选择 `GitHub.com` → `HTTPS` → `Login with a web browser`
> Chọn `GitHub.com` → `HTTPS` → `Login with a web browser`

---

## 🚀 安装 Skills / Cài đặt Skills

### 查看所有可用 Skills / Xem danh sách Skills
```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- --list
```

### 安装全部 / Cài tất cả
```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash
```

### 只安装指定的 / Chỉ cài những cái cần
```bash
# 示例：只装翻译和PPT / Ví dụ: chỉ cài phiên dịch và PPT
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 小玲翻译 NIVEX_PPT
```

### 更新已安装的 Skill / Cập nhật Skill đã cài
重新运行安装命令即可，会自动覆盖旧版本。
Chạy lại lệnh cài đặt, phiên bản cũ sẽ tự động được ghi đè.

---

## 📋 Skills 分类 / Phân loại Skills theo vị trí

### 🎯 销售 & 客服 / Kinh doanh & CSKH

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả | 适合谁 / Ai nên dùng |
|-------|----------------------|-------------|---------------------|
| `AK_投资顾问` | AK、投资顾问 | 客户咨询应答、异议处理话术、客户分类跟进 — Tư vấn khách hàng, xử lý phản đối, phân loại & theo dõi | 销售、客服 / Sales, CSKH |

```bash
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- AK_投资顾问
```

---

### 🌐 翻译 & 语言 / Phiên dịch & Ngôn ngữ

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả | 适合谁 / Ai nên dùng |
|-------|----------------------|-------------|---------------------|
| `小玲翻译` | 小玲翻译、翻译一下 | 中越双语翻译，注重语气和场景适配 — Dịch Trung-Việt, chú trọng ngữ khí và ngữ cảnh | 翻译、运营 / Phiên dịch, Vận hành |
| `芳草_翻译助理` | 芳草翻译 | 翻译助理，会议纪要、文档翻译 — Trợ lý dịch thuật, biên bản họp, dịch tài liệu | 翻译、行政 / Phiên dịch, Hành chính |
| `交易所语言QA` | 语言QA、翻译审查 | 多语言翻译质量审查（越/韩/日/泰） — Kiểm tra chất lượng dịch đa ngôn ngữ (Việt/Hàn/Nhật/Thái) | 翻译、产品 / Phiên dịch, Product |

```bash
# 安装全部翻译相关 / Cài tất cả liên quan phiên dịch
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 小玲翻译 芳草_翻译助理 交易所语言QA
```

---

### 📊 市场 & 运营 / Marketing & Vận hành

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả | 适合谁 / Ai nên dùng |
|-------|----------------------|-------------|---------------------|
| `市场速递` | 市场速递、日报 | 每日 BTC/ETH 行情分析 + 中越双语策略 — Phân tích BTC/ETH hàng ngày + chiến lược song ngữ Trung-Việt | 市场、运营 / Marketing, Vận hành |
| `NIVEX_PPT` | 做PPT、生成PPT | HTML 演示文稿生成，暗色科技风 — Tạo slide HTML, phong cách công nghệ tối | 市场、管理层 / Marketing, Quản lý |

```bash
# 安装市场运营套装 / Cài bộ Marketing & Vận hành
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 市场速递 NIVEX_PPT
```

---

### 🏢 管理 / Quản lý

| Skill | 触发词 / Từ kích hoạt | 说明 / Mô tả | 适合谁 / Ai nên dùng |
|-------|----------------------|-------------|---------------------|
| `业务工作流` | 做工作流、流程拆解 | 目标倒推 → 流程拆解 → KPI → 树状图输出 — Đảo ngược mục tiêu → Tách quy trình → KPI → Xuất sơ đồ cây | 管理层 / Quản lý |
| `员工Skill评分` | Skill评分 | 员工能力评估打分系统 — Hệ thống đánh giá năng lực nhân viên | HR、管理层 / HR, Quản lý |

```bash
# 安装管理套装 / Cài bộ Quản lý
curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 业务工作流 员工Skill评分
```

---

## 🔧 使用方法 / Cách sử dụng

安装完成后，打开 Claude Code，直接说触发词即可：
Sau khi cài xong, mở Claude Code và nói từ kích hoạt:

```
# 示例 / Ví dụ:
> 小玲翻译，帮我翻译一下这段话
> 做个PPT，主题是交易所介绍
> AK，这个客户问安全性怎么回答
> 市场速递
```

---

## 🤝 贡献新 Skill / Đóng góp Skill mới

想给团队添加新 Skill？按以下步骤：
Muốn thêm Skill mới cho team? Làm theo các bước sau:

1. **Fork** 这个仓库 / Fork repo này
2. 在 `skills/` 下创建文件夹，必须包含 `SKILL.md` / Tạo thư mục trong `skills/`, phải có file `SKILL.md`
3. 提交 **Pull Request**，管理员审核后合并 / Gửi **Pull Request**, admin review xong sẽ merge

### Skill 文件夹结构 / Cấu trúc thư mục Skill
```
skills/
  你的Skill名/
    SKILL.md          ← 必须 / Bắt buộc (主规则文件)
    规则/              ← 可选 / Tùy chọn
    模板/              ← 可选 / Tùy chọn
    术语表/            ← 可选 / Tùy chọn
```

---

## ❓ 常见问题 / Câu hỏi thường gặp

**Q: 安装后找不到 Skill？/ Cài xong không thấy Skill?**
> 重启 Claude Code 即可。/ Khởi động lại Claude Code.

**Q: 怎么更新到最新版本？/ Làm sao cập nhật phiên bản mới nhất?**
> 重新运行安装命令，会自动覆盖。/ Chạy lại lệnh cài đặt, tự động ghi đè.

**Q: 可以同时安装多个吗？/ Có thể cài nhiều cái cùng lúc không?**
> 可以，名称用空格隔开。/ Được, cách nhau bằng dấu cách.
> `bash -s -- 小玲翻译 NIVEX_PPT AK_投资顾问`

**Q: 安装报错 `gh auth` 失败？/ Lỗi `gh auth` khi cài?**
> 先运行 `gh auth login` 登录 GitHub。/ Chạy `gh auth login` để đăng nhập GitHub trước.

**Q: 我不是技术人员，不会用终端？/ Tôi không biết dùng terminal?**
> 复制上面的命令，粘贴到终端（Mac: Terminal / Win: PowerShell）按回车就行。
> Copy lệnh ở trên, dán vào terminal (Mac: Terminal / Win: PowerShell) rồi nhấn Enter.
