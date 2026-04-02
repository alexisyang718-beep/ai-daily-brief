#!/bin/bash
# Step 4: 发布（GitHub + 测试邮件 + 公众号，三步同时）
# 用法：bash scripts/step4-publish.sh brief/2026-04-01.html

cd "$(dirname "$0")/.."

# 确定日报文件
if [ -n "$1" ]; then
  BRIEF_FILE="$1"
else
  BRIEF_FILE=$(ls brief/????-??-??.html 2>/dev/null | sort -r | head -1)
  if [ -z "$BRIEF_FILE" ]; then
    echo "❌ 没有找到日报文件，请指定：bash scripts/step4-publish.sh brief/YYYY-MM-DD.html"
    exit 1
  fi
  echo "⚡ 自动检测到最新日报：$BRIEF_FILE"
fi

if [ ! -f "$BRIEF_FILE" ]; then
  echo "❌ 文件不存在：$BRIEF_FILE"
  exit 1
fi

echo ""
echo "================================================================"
echo "  STEP 4: 发布同步"
echo "  文件：$BRIEF_FILE"
echo "================================================================"
echo ""
echo "将执行以下三步（同时进行）："
echo "  1. GitHub push"
echo "  2. 发送测试邮件 → alexisyang@tencent.com"
echo "  3. 同步公众号草稿箱"
echo ""
echo "完成后请确认测试邮件，再运行 step4-sendall.sh 群发"
echo ""

python3 scripts/publish_all.py "$BRIEF_FILE"
