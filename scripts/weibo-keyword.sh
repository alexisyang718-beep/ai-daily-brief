#!/bin/bash
# 微博热搜关键词过滤
# 用法: ./weibo-keyword.sh "关键词" [数量]

KEYWORD="${1:-AI}"
COUNT="${2:-50}"

~/.local/bin/weibo hot -n "$COUNT" --json 2>/dev/null | python3 -c "
import sys, json

data = json.load(sys.stdin)
keyword = '$KEYWORD'.lower()
items = data.get('realtime', [])[:$COUNT]

results = [item for item in items if keyword in item.get('word', '').lower()]

print(f'找到 {len(results)} 条包含 \"$KEYWORD\" 的热搜:\n')
for i, item in enumerate(results, 1):
    word = item.get('word', '')
    icon = item.get('icon_desc', '')
    num = item.get('num', '')
    print(f'{i}. {word} {icon} {num}')
"
