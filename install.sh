#!/bin/bash
# NIVEX Skills 安装脚本
#
# 用法:
#   安装全部:  bash install.sh
#   安装指定:  bash install.sh 小玲翻译 NIVEX_PPT
#   查看列表:  bash install.sh --list
#
# 远程执行:
#   全部:  curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash
#   指定:  curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 小玲翻译 NIVEX_PPT
#   列表:  curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- --list

set -e

SKILLS_DIR="$HOME/.claude/skills"
REPO_URL="https://github.com/a2320661034-ops/nivex-skills.git"
TMP_DIR=$(mktemp -d)

# 检查 gh 登录状态
if ! gh auth status &>/dev/null; then
  echo "❌ 请先登录 GitHub: gh auth login"
  exit 1
fi

# 克隆仓库
echo "📦 拉取 Skills 仓库..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR/repo" 2>/dev/null

# --list 模式：只列出可用 Skills
if [ "$1" = "--list" ]; then
  echo ""
  echo "📋 可用 Skills："
  echo "─────────────────"
  for skill in "$TMP_DIR/repo/skills/"*/; do
    skill_name=$(basename "$skill")
    # 读取 SKILL.md 第一行作为简介
    desc=$(head -1 "$skill/SKILL.md" 2>/dev/null | sed 's/^#\+ *//')
    echo "  • $skill_name  —  $desc"
  done
  echo ""
  echo "安装指定 Skill:  bash install.sh <名称1> <名称2> ..."
  rm -rf "$TMP_DIR"
  exit 0
fi

mkdir -p "$SKILLS_DIR"
installed=0

if [ $# -eq 0 ]; then
  # 无参数：安装全部
  echo "🔧 安装全部 Skills..."
  echo ""
  for skill in "$TMP_DIR/repo/skills/"*/; do
    skill_name=$(basename "$skill")
    [ -d "$SKILLS_DIR/$skill_name" ] && rm -rf "$SKILLS_DIR/$skill_name"
    cp -r "$skill" "$SKILLS_DIR/$skill_name"
    echo "  ✓ $skill_name"
    installed=$((installed + 1))
  done
else
  # 有参数：只安装指定的
  echo "🔧 安装选定 Skills..."
  echo ""
  for skill_name in "$@"; do
    src="$TMP_DIR/repo/skills/$skill_name"
    if [ -d "$src" ]; then
      [ -d "$SKILLS_DIR/$skill_name" ] && rm -rf "$SKILLS_DIR/$skill_name"
      cp -r "$src" "$SKILLS_DIR/$skill_name"
      echo "  ✓ $skill_name"
      installed=$((installed + 1))
    else
      echo "  ✗ $skill_name — 不存在，跳过"
      echo "    用 --list 查看可用列表"
    fi
  done
fi

rm -rf "$TMP_DIR"

echo ""
echo "✅ 完成！安装了 $installed 个 Skills"
echo "📍 位置: $SKILLS_DIR"
