#!/bin/bash
# Step 2: 选题
# 用法：在AI对话开始时运行此脚本，输出的内容就是AI的上下文

cd "$(dirname "$0")/.."

COLLECT_OUTPUT=$(ls collect/output/*.md 2>/dev/null | sort -r | head -1)

echo "================================================================"
echo "  STEP 2: 选题"
echo "================================================================"
echo ""
echo "【采集文件】"
if [ -n "$COLLECT_OUTPUT" ]; then
  echo "  $COLLECT_OUTPUT"
else
  echo "  ⚠️  collect/output/ 下没有找到采集文件，请先运行 Step 1："
  echo "  python3 collect/collect.py"
  exit 1
fi

echo ""
echo "================================================================"
echo "  选题规则（必须遵守）"
echo "================================================================"
echo ""
cat workflow/02-selection/news-preferences.md

echo ""
echo "================================================================"
echo "  执行说明"
echo "================================================================"
echo "1. 读取上方采集文件内容"
echo "2. 按照上方选题规则筛选新闻"
echo "3. 输出选题报告，格式如下："
echo ""
echo "   ## 信源质量汇总"
echo "   | 信源 | 采集条数 | 入选 | 筛掉 | 筛掉原因 |"
echo "   （每个出现在采集报告里的信源都要有一行）"
echo ""
echo "   ## 入选新闻（共X条）"
echo "   每条格式：板块 / 标题 / 来源 / 理由"
echo ""
echo "   ## 待确认（可选，有疑问的条目）"
echo ""
echo "4. 保存到：selection/selection_$(date +%Y%m%d).md"
echo "5. 等待人工确认后，再运行 step3-writing.sh"
echo "================================================================"
