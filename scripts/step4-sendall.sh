#!/bin/bash
# Step 4 群发：确认测试邮件OK后才能执行
# 用法：bash scripts/step4-sendall.sh brief/2026-04-01.html

cd "$(dirname "$0")/.."

# 确定日报文件
if [ -n "$1" ]; then
  BRIEF_FILE="$1"
else
  BRIEF_FILE=$(ls brief/????-??-??.html 2>/dev/null | sort -r | head -1)
  if [ -z "$BRIEF_FILE" ]; then
    echo "❌ 没有找到日报文件，请指定：bash scripts/step4-sendall.sh brief/YYYY-MM-DD.html"
    exit 1
  fi
fi

if [ ! -f "$BRIEF_FILE" ]; then
  echo "❌ 文件不存在：$BRIEF_FILE"
  exit 1
fi

echo ""
echo "================================================================"
echo "  群发确认"
echo "================================================================"
echo ""
echo "  日报文件：$BRIEF_FILE"
echo ""

# 显示收件人列表
RECIPIENTS=$(python3 -c "
import yaml
with open('config/config.yaml') as f:
    cfg = yaml.safe_load(f)
for r in cfg['email']['recipients']:
    print('  -', r)
" 2>/dev/null)

echo "  收件人列表："
echo "$RECIPIENTS"
echo ""
echo "  ⚠️  此操作将向以上所有人发送邮件，无法撤回"
echo ""
echo -n "  请输入 yes 确认群发："
read CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo ""
  echo "  已取消。"
  exit 0
fi

echo ""
echo "正在群发..."
python3 scripts/publish_all.py "$BRIEF_FILE" --send-all
