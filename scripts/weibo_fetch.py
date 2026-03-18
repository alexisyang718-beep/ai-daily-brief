#!/usr/bin/env python3
"""
微博采集脚本
用法：
  python scripts/weibo_fetch.py              # 采集配置文件中所有博主的微博
  python scripts/weibo_fetch.py --user "数码闲聊站"  # 只采集指定博主
  python scripts/weibo_fetch.py --json       # 输出 JSON 格式
  python scripts/weibo_fetch.py --yaml       # 输出 YAML 格式（默认）
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml


def get_weibo_cli_path():
    """获取 weibo-cli 路径"""
    # 优先使用用户目录下的 weibo
    weibo_path = Path.home() / ".local" / "bin" / "weibo"
    if weibo_path.exists():
        return str(weibo_path)
    # 回退到系统 PATH
    return "weibo"


def search_weibo(query, max_results=10):
    """使用 weibo-cli 搜索微博"""
    weibo_cmd = get_weibo_cli_path()

    cmd = [weibo_cmd, "search", query, "-n", str(max_results), "--json"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PATH": "/Users/yangliu/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"}
        )

        if result.returncode != 0:
            print(f"搜索 '{query}' 失败: {result.stderr}", file=sys.stderr)
            return []

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout)
            return data.get("statuses", [])
        except json.JSONDecodeError as e:
            print(f"解析 JSON 失败: {e}", file=sys.stderr)
            print(f"原始输出: {result.stdout[:500]}", file=sys.stderr)
            return []

    except subprocess.TimeoutExpired:
        print(f"搜索 '{query}' 超时", file=sys.stderr)
        return []
    except Exception as e:
        print(f"搜索 '{query}' 出错: {e}", file=sys.stderr)
        return []


def fetch_user_weibo(username, max_results=10):
    """获取指定用户发布的微博（通过搜索用户名）"""
    # 搜索用户名，获取该用户发布的内容
    return search_weibo(f'"{username}"', max_results)


def load_config():
    """加载微博用户配置文件"""
    config_path = Path(__file__).parent.parent / "config" / "weibo_users.yaml"

    if not config_path.exists():
        print(f"配置文件不存在: {config_path}", file=sys.stderr)
        return {"weibo_users": [], "settings": {"max_weibos_per_user": 10}}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_weibo(weibo, username):
    """格式化单条微博为结构化字典"""
    user = weibo.get("user", {})
    created_at = weibo.get("created_at", "")

    # 尝试解析时间
    try:
        # 微博时间格式：Thu Mar 16 10:30:00 +0800 2026
        dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        created_at = dt.strftime("%Y-%m-%d %H:%M")
    except:
        pass

    return {
        "id": weibo.get("id"),
        "mid": weibo.get("mblogid", ""),
        "username": username,
        "nickname": user.get("screen_name", username),
        "content": weibo.get("text", ""),
        "content_raw": weibo.get("text_raw", weibo.get("text", "")),
        "created_at": created_at,
        "source": weibo.get("source", ""),
        "reposts_count": weibo.get("reposts_count", 0),
        "comments_count": weibo.get("comments_count", 0),
        "attitudes_count": weibo.get("attitudes_count", 0),
        "pic_urls": [p.get("large", {}).get("url", p.get("url", "")) for p in weibo.get("pic_urls", [])],
        "pics": weibo.get("pic_num", 0),
        "video": weibo.get("video_info", {}).get("video_url", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="微博采集脚本")
    parser.add_argument("--user", "-u", help="指定要采集的用户名（跳过配置文件）")
    parser.add_argument("--json", "-j", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--yaml", "-y", action="store_true", help="输出 YAML 格式（默认）")
    parser.add_argument("--max", "-n", type=int, default=10, help="每个用户最多采集条数（默认10）")
    parser.add_argument("--limit", "-l", type=int, help="限制总采集用户数（用于测试）")
    args = parser.parse_args()

    # 获取最大条数配置
    max_per_user = args.max

    results = {
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "weibo",
        "users": []
    }

    # 确定要采集的用户列表
    users_to_fetch = []

    if args.user:
        # 命令行指定用户
        users_to_fetch = [{"name": args.user, "category": "命令行指定"}]
    else:
        # 加载配置文件
        config = load_config()
        settings = config.get("settings", {})
        max_per_user = args.max if args.max != 10 else settings.get("max_weibos_per_user", 10)

        for user in config.get("weibo_users", []):
            users_to_fetch.append(user)

        if not users_to_fetch:
            print("未配置要采集的微博用户", file=sys.stderr)
            sys.exit(1)

    # 限制用户数（用于测试）
    if args.limit:
        users_to_fetch = users_to_fetch[:args.limit]

    print(f"开始采集 {len(users_to_fetch)} 个微博用户的最新微博...", file=sys.stderr)

    for i, user in enumerate(users_to_fetch, 1):
        username = user.get("name", "")
        category = user.get("category", "未知")

        if not username:
            continue

        print(f"[{i}/{len(users_to_fetch)}] 采集 @{username} ({category})...", file=sys.stderr)

        weibos = fetch_user_weibo(username, max_per_user)

        # 过滤只保留该用户发布的微博（通过昵称匹配）
        user_weibos = []
        for w in weibos:
            w_user = w.get("user", {})
            w_nickname = w_user.get("screen_name", "")
            # 检查是否是该用户发布的
            if w_nickname == username or w_nickname.find(username) >= 0:
                user_weibos.append(format_weibo(w, username))

        # 如果搜索没找到用户发的，就用搜索结果的前几条
        if not user_weibos and weibos:
            print(f"  警告：未精确匹配到 @{username}，使用搜索结果", file=sys.stderr)
            user_weibos = [format_weibo(w, username) for w in weibos[:max_per_user]]

        results["users"].append({
            "username": username,
            "uid": user.get("uid", ""),
            "category": category,
            "description": user.get("description", ""),
            "count": len(user_weibos),
            "weibos": user_weibos
        })

        print(f"  获取到 {len(user_weibos)} 条微博", file=sys.stderr)

        # 避免请求过快
        if i < len(users_to_fetch):
            time.sleep(1)

    # 统计
    total_weibos = sum(u["count"] for u in results["users"])
    results["summary"] = {
        "total_users": len(results["users"]),
        "total_weibos": total_weibos
    }

    # 输出
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # YAML 格式
        print(yaml.dump(results, allow_unicode=True, default_flow_style=False))


if __name__ == "__main__":
    main()
