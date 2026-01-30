#!/bin/bash
# NIVEX Skills 安装脚本
#
# 用法:
#   安装全部:  curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash
#   安装指定:  curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- 小玲翻译 NIVEX_PPT
#   查看列表:  curl -sL https://raw.githubusercontent.com/a2320661034-ops/nivex-skills/main/install.sh | bash -s -- --list

set -e

SKILLS_DIR="$HOME/.claude/skills"
REPO="a2320661034-ops/nivex-skills"
TMP_DIR=$(mktemp -d)

# 下载仓库（zip，不需要 git 或 gh）
echo "📦 下载 Skills..."
curl -sL "https://github.com/$REPO/archive/refs/heads/main.zip" -o "$TMP_DIR/skills.zip"
unzip -q "$TMP_DIR/skills.zip" -d "$TMP_DIR"
SRC="$TMP_DIR/nivex-skills-main/skills"

if [ ! -d "$SRC" ]; then
  echo "❌ 下载失败，请检查网络"
  rm -rf "$TMP_DIR"
  exit 1
fi

# --list 模式
if [ "$1" = "--list" ]; then
  echo ""
  echo "📋 可用 Skills："
  echo "─────────────────"
  for skill in "$SRC"/*/; do
    skill_name=$(basename "$skill")
    desc=$(head -1 "$skill/SKILL.md" 2>/dev/null | sed 's/^#\+ *//')
    echo "  • $skill_name  —  $desc"
  done
  echo ""
  echo "安装指定 Skill / Cài Skill chỉ định:"
  echo "  curl -sL https://raw.githubusercontent.com/$REPO/main/install.sh | bash -s -- <名称>"
  rm -rf "$TMP_DIR"
  exit 0
fi

mkdir -p "$SKILLS_DIR"
installed=0

if [ $# -eq 0 ]; then
  echo "🔧 安装全部 Skills / Cài tất cả..."
  echo ""
  for skill in "$SRC"/*/; do
    skill_name=$(basename "$skill")
    [ -d "$SKILLS_DIR/$skill_name" ] && rm -rf "$SKILLS_DIR/$skill_name"
    cp -r "$skill" "$SKILLS_DIR/$skill_name"
    echo "  ✓ $skill_name"
    installed=$((installed + 1))
  done
else
  echo "🔧 安装选定 Skills / Cài Skills đã chọn..."
  echo ""
  for skill_name in "$@"; do
    src="$SRC/$skill_name"
    if [ -d "$src" ]; then
      [ -d "$SKILLS_DIR/$skill_name" ] && rm -rf "$SKILLS_DIR/$skill_name"
      cp -r "$src" "$SKILLS_DIR/$skill_name"
      echo "  ✓ $skill_name"
      installed=$((installed + 1))
    else
      echo "  ✗ $skill_name — 不存在 / Không tồn tại"
      echo "    用 --list 查看列表 / Dùng --list để xem danh sách"
    fi
  done
fi

rm -rf "$TMP_DIR"

echo ""
echo "✅ 完成！安装了 $installed 个 Skills / Hoàn tất! Đã cài $installed Skills"
echo "📍 位置 / Vị trí: $SKILLS_DIR"
echo ""
echo "💡 打开 Claude Code 桌面版即可使用 / Mở Claude Code Desktop để sử dụng"
