#!/bin/bash
# NIVEX Skills 一键安装脚本
# 用法: curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash

set -e

SKILLS_DIR="$HOME/.claude/skills"
REPO_URL="https://github.com/a2320661034-ops/nivex-skills.git"
TMP_DIR=$(mktemp -d)

echo "🔧 NIVEX Skills 安装中..."

# 检查 gh 登录状态
if ! gh auth status &>/dev/null; then
  echo "❌ 请先登录 GitHub: gh auth login"
  exit 1
fi

# 克隆仓库
git clone --depth 1 "$REPO_URL" "$TMP_DIR/repo" 2>/dev/null

# 创建目标目录
mkdir -p "$SKILLS_DIR"

# 复制所有 skill
for skill in "$TMP_DIR/repo/skills/"*/; do
  skill_name=$(basename "$skill")
  if [ -d "$SKILLS_DIR/$skill_name" ]; then
    echo "⚠️  $skill_name 已存在，覆盖更新"
    rm -rf "$SKILLS_DIR/$skill_name"
  fi
  cp -r "$skill" "$SKILLS_DIR/$skill_name"
  echo "✓ $skill_name"
done

# 清理
rm -rf "$TMP_DIR"

echo ""
echo "✅ 安装完成！共安装 $(ls -d "$SKILLS_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ') 个 Skills"
echo "📍 位置: $SKILLS_DIR"
