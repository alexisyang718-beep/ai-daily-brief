#!/usr/bin/env python3
"""Filter and curate important tweets from raw timeline data."""
import json
import sys

RAW_FILE = '/Users/yangliu/Documents/Claude Code/codebuddy/tech-daily-brief/output/twitter_raw_20260318.json'
OUT_FILE = '/Users/yangliu/Documents/Claude Code/codebuddy/tech-daily-brief/output/twitter_curated_20260318.json'

with open(RAW_FILE) as f:
    data = json.load(f)

ai_keywords = [
    'ai', 'gpt', 'claude', 'openai', 'nvidia', 'gtc', 'gemini', 'model', 'agent',
    'llm', 'manus', 'openclaw', 'deepseek', 'anthropic', 'robot', 'chip',
    'hermes', 'molmo', 'nemo', 'dispatch', 'cowork', 'computer-use',
    'inference', 'training', 'open-source', 'open source', '开源', '大模型',
    '人工智能', '芯片', 'meta', 'apple', 'google', 'microsoft', 'hugging',
    'cerebras', 'coding', 'copilot', 'cursor', 'vscode', '龙虾', 'claw',
    'reasoning', 'benchmark', 'agentic', 'fine-tun', 'rag', 'mcp',
    'tesla', 'xpeng', '小鹏', 'humanoid', '机器人', 'game', '游戏',
    'grok', 'nous', 'scaling', 'token', '模型', 'api'
]

important_accounts = [
    'dotey', 'sama', 'OpenAI', 'OpenAIDevs', 'AnthropicAI', 'GoogleDeepMind',
    'nvidia', 'NVIDIADC', 'karpathy', 'DrJimFan', 'ylecun', 'hardmaru',
    'fxtrader', 'TheRundownAI', 'allen_ai', 'NousResearch', 'Teknium',
    'shao__meng', 'runes_leo', 'xiaohu', 'Saboo_Shubham_', 'vast_ai',
    'XPengMotors', 'cnfinancewatch', 'garrytan', 'nvidianewsroom'
]

important = []
for t in data:
    text = t.get('text', '').lower()
    sn = t.get('author', {}).get('screenName', '')
    views = t.get('metrics', {}).get('views', 0) or 0
    likes = t.get('metrics', {}).get('likes', 0) or 0
    rtby = t.get('retweetedBy', '') or ''

    is_ai = any(kw in text for kw in ai_keywords)
    is_vip = sn in important_accounts or rtby in important_accounts
    is_hot = views > 5000 or likes > 50

    if is_ai or is_vip or is_hot:
        important.append(t)

important.sort(key=lambda x: (x.get('metrics', {}).get('views', 0) or 0), reverse=True)

print(f'筛选结果: {len(important)} 条重要推文 (总共 {len(data)} 条)\n')

output = []
for t in important:
    a = t.get('author', {})
    entry = {
        'author': f"@{a.get('screenName', '')} ({a.get('name', '')})",
        'text': t.get('text', ''),
        'time': t.get('createdAtLocal', ''),
        'views': t.get('metrics', {}).get('views', 0),
        'likes': t.get('metrics', {}).get('likes', 0),
        'retweets': t.get('metrics', {}).get('retweets', 0),
        'isRetweet': t.get('isRetweet', False),
        'retweetedBy': t.get('retweetedBy', ''),
        'urls': t.get('urls', []),
        'media': t.get('media', [])
    }
    output.append(entry)

    rt_tag = f" [RT by {t.get('retweetedBy', '')}]" if t.get('isRetweet') else ""
    short = entry['text'][:150].replace('\n', ' ')
    print(f"- {entry['author']}{rt_tag} [{entry['time']}] views:{entry['views']:,} likes:{entry['likes']}")
    print(f"  {short}")
    print()

with open(OUT_FILE, 'w') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f'\nSaved {len(output)} curated tweets to {OUT_FILE}')
