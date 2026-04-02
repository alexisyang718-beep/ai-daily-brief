#!/bin/bash
# Step 3: 撰写日报
# 用法：在AI对话开始时运行此脚本，输出的内容就是AI的上下文

cd "$(dirname "$0")/.."

DATE=$(date +%Y%m%d)
SELECTION_FILE="selection/selection_${DATE}.md"

echo "================================================================"
echo "  STEP 3: 撰写日报"
echo "================================================================"
echo ""

# 检查选题文件
echo "【选题文件】"
if [ -f "$SELECTION_FILE" ]; then
  echo "  ✅ $SELECTION_FILE"
else
  # 找最新的选题文件
  LATEST=$(ls selection/selection_*.md 2>/dev/null | sort -r | head -1)
  if [ -n "$LATEST" ]; then
    echo "  ⚠️  今日选题文件不存在，找到最新的："
    echo "  $LATEST"
    SELECTION_FILE="$LATEST"
  else
    echo "  ❌ selection/ 下没有找到选题文件，请先完成 Step 2"
    exit 1
  fi
fi

echo ""
echo "【模板文件】"
echo "  template.html（必须读取，禁止自行创建HTML结构）"

echo ""
echo "================================================================"
echo "  撰写规则（必须遵守）"
echo "================================================================"
echo ""
cat workflow/03-generation/writing-preferences.md

echo ""
echo "================================================================"
echo "  执行说明"
echo "================================================================"
echo "1. 读取选题文件：$SELECTION_FILE"
echo "2. 读取模板：template.html"
echo "3. 严格按照上方撰写规则撰写"
echo "4. 输出日报：brief/$(date +%Y-%m-%d).html"
echo "================================================================"
