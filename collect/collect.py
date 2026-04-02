#!/usr/bin/env python3
"""
daily-brief-collector / collect.py
早上运行一次，采集过去48小时的内容，输出分层 Markdown。

用法：
    python3 collect.py              # 采集全部（官方 + 媒体 + X）
    python3 collect.py --skip-x    # 跳过 X（网络不好时）
    python3 collect.py --hours 72  # 扩大时间窗口到72小时
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import yaml

# ── 路径 ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
SOURCES    = BASE_DIR / "sources" / "sources.yaml"
FILTERS    = BASE_DIR / "sources" / "filters.yaml"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR    = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ── 时区 ──────────────────────────────────────────────────────────────────────
CST = timezone(timedelta(hours=8))

def now_cst():
    return datetime.now(CST)

def to_cst(dt):
    """把任意 aware/naive datetime 转成 CST。"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CST)

def time_ago(dt):
    """返回人类可读的相对时间，如 '3小时前'。"""
    if dt is None:
        return "时间未知"
    delta = now_cst() - to_cst(dt)
    secs = delta.total_seconds()
    if secs < 0:
        return "刚刚"   # 时区偏差导致"未来"时间，当作刚发布处理
    hours = secs / 3600
    if hours < 1:
        return f"{int(secs / 60)}分钟前"
    if hours < 24:
        return f"{int(hours)}小时前"
    return f"{int(hours / 24)}天前"

# ── 加载配置 ──────────────────────────────────────────────────────────────────
def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

# ── 粗筛 ──────────────────────────────────────────────────────────────────────
def build_exclude_patterns(filters_cfg):
    patterns = []
    for kw in filters_cfg.get("exclude", []):
        kw_stripped = kw.strip()
        if kw != kw_stripped:
            # 原关键词带空格（如 " election "），用 \b 词边界防止误伤子串
            # 例：" election " → \belection\b，不会匹配 "selection"
            pattern = r'\b' + re.escape(kw_stripped) + r'\b'
        else:
            pattern = re.escape(kw_stripped)
        patterns.append(re.compile(pattern, re.IGNORECASE))
    return patterns

def should_exclude(text, patterns):
    for p in patterns:
        if p.search(text):
            return True, p.pattern
    return False, None

# ── RSS 采集 ──────────────────────────────────────────────────────────────────
def fetch_rss(url, entity, hours, exclude_patterns):
    """
    返回 (items, stats)
    items: list of dict {title, url, published, entity, domain}
    stats: dict {in_window, filtered, kept, failed_reason}
      in_window  — 时效性通过的条数
      filtered   — 被关键词过滤掉的条数
      kept       — 最终保留条数
    """
    cutoff = now_cst() - timedelta(hours=hours)

    try:
        feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        return [], {"in_window": 0, "filtered": 0, "kept": 0, "failed_reason": str(e)}

    if feed.bozo and not feed.entries:
        reason = str(feed.bozo_exception) if hasattr(feed, "bozo_exception") else "解析失败"
        return [], {"in_window": 0, "filtered": 0, "kept": 0, "failed_reason": reason}

    domain = urlparse(url).netloc
    items = []
    in_window = 0
    filtered  = 0

    for entry in feed.entries:
        # 解析发布时间
        pub = None
        for attr in ("published_parsed", "updated_parsed", "created_parsed"):
            val = getattr(entry, attr, None)
            if val:
                import time as _time
                pub = datetime(*val[:6], tzinfo=timezone.utc)
                break

        # 时效性过滤
        if pub and to_cst(pub) < cutoff:
            continue

        in_window += 1
        title = getattr(entry, "title", "").strip()
        link  = getattr(entry, "link",  "").strip()
        summary = getattr(entry, "summary", "") or ""
        summary_text = re.sub(r"<[^>]+>", " ", summary)
        check_text = f"{title} {summary_text}"

        excluded, matched = should_exclude(check_text, exclude_patterns)
        if excluded:
            filtered += 1
            continue

        items.append({
            "title":     title,
            "url":       link,
            "published": pub,
            "entity":    entity,
            "domain":    domain,
        })

    return items, {"in_window": in_window, "filtered": filtered, "kept": len(items), "failed_reason": None}


def fetch_layer(layer_sources, hours, exclude_patterns, layer_label):
    """采集一整层（官方 or 媒体），返回 all_items 和 status_lines。"""
    all_items    = []
    status_lines = []

    for source in layer_sources:
        entity = source["entity"]
        url    = source["url"]
        items, stats = fetch_rss(url, entity, hours, exclude_patterns)

        if stats["failed_reason"]:
            line = f"  ❌ {entity} — {stats['failed_reason']}"
        else:
            in_w     = stats["in_window"]
            filtered = stats["filtered"]
            kept     = stats["kept"]
            if in_w == 0:
                line = f"  ⚪ {entity} — {hours}h内无新内容"
            elif filtered == 0:
                line = f"  ✅ {entity} — 时效{in_w}条 → 保留{kept}条"
            else:
                line = f"  ✅ {entity} — 时效{in_w}条 → 过滤{filtered}条 → 保留{kept}条"
            all_items.extend(items)

        print(line)
        status_lines.append(line)

    return all_items, status_lines


# ── X 采集（twitter-cli）─────────────────────────────────────────────────────
TWITTER_CLI = os.path.expanduser("~/.local/bin/twitter")
PATH_ENV = (
    os.path.expanduser("~/.local/bin") + ":"
    + "/Library/Frameworks/Python.framework/Versions/3.13/bin:"
    + "/usr/local/bin:/usr/bin:/bin"
)

def fetch_x_account(handle, hours, exclude_patterns):
    """
    用 twitter-cli 采集单个账号最近推文。
    返回 (items, error_msg)
    """
    cutoff = now_cst() - timedelta(hours=hours)
    try:
        result = subprocess.run(
            [TWITTER_CLI, "user-posts", handle, "--json", "-n", "20"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PATH": PATH_ENV},
        )
        if result.returncode != 0:
            return [], result.stderr.strip() or "非零退出码"

        import json
        parsed = json.loads(result.stdout)
        # 新格式：{"ok": true, "data": [...]}
        if isinstance(parsed, dict):
            if not parsed.get("ok"):
                return [], parsed.get("error", "API返回错误")
            tweets = parsed.get("data", [])
        elif isinstance(parsed, list):
            tweets = parsed
        else:
            return [], "未知JSON格式"

    except subprocess.TimeoutExpired:
        return [], "超时"
    except Exception as e:
        return [], str(e)

    items = []
    for tw in tweets:
        text     = tw.get("text", "")
        tweet_id = tw.get("id", "")
        # 新格式使用 createdAtISO
        created  = tw.get("createdAtISO") or tw.get("created_at", "")
        url      = f"https://x.com/{handle}/status/{tweet_id}" if tweet_id else ""

        # 跳过转推
        if tw.get("isRetweet") or text.startswith("RT @"):
            continue

        # 时效性
        pub = None
        if created:
            try:
                from datetime import datetime
                # ISO格式：2026-03-30T15:34:16+00:00
                pub = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                try:
                    pub = datetime.strptime(created, "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=timezone.utc)
                except Exception:
                    pass
        if pub and to_cst(pub) < cutoff:
            continue

        excluded, _ = should_exclude(text, exclude_patterns)
        if excluded:
            continue

        items.append({
            "title":     text[:140] + ("…" if len(text) > 140 else ""),
            "url":       url,
            "published": pub,
            "entity":    f"@{handle}",
            "domain":    "x.com",
        })

    return items, None


def fetch_x_layer(x_cfg, hours, exclude_patterns):
    all_items    = []
    status_lines = []

    for priority in ("p1_must", "p2_optional"):
        accounts = x_cfg.get(priority, [])
        for acc in accounts:
            handle = acc["handle"]
            items, err = fetch_x_account(handle, hours, exclude_patterns)
            if err:
                tag  = "❌" if priority == "p1_must" else "⚠️"
                line = f"  {tag} @{handle} — {err}"
            else:
                line = f"  ✅ @{handle} — 保留{len(items)}条"
                all_items.extend(items)
            print(line)
            status_lines.append(line)

    return all_items, status_lines


# ── 微博采集（weibo-cli）────────────────────────────────────────────────────
WEIBO_CLI = os.path.expanduser("~/.local/bin/weibo")

def fetch_weibo_account(name, uid, hours, exclude_patterns):
    """
    用 weibo-cli 采集单个微博账号。
    返回 (items, error_msg)
    """
    import json as _json
    cutoff = now_cst() - timedelta(hours=hours)
    env = {**os.environ, "PATH": PATH_ENV}

    try:
        result = subprocess.run(
            [WEIBO_CLI, "weibos", str(uid), "-n", "20", "--json"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        if result.returncode != 0:
            return [], result.stderr.strip() or "非零退出码"
        data = _json.loads(result.stdout)
        weibos = data.get("list", []) if isinstance(data, dict) else data
    except subprocess.TimeoutExpired:
        return [], "超时"
    except Exception as e:
        return [], str(e)

    items = []
    for w in weibos:
        text = w.get("text_raw") or w.get("text", "")
        # 去除 HTML 标签
        text = re.sub(r"<[^>]+>", " ", text).strip()

        # 时效性
        created = w.get("created_at", "")
        pub = None
        if created:
            try:
                pub = datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")
            except Exception:
                pass
        if pub and to_cst(pub) < cutoff:
            continue

        excluded, _ = should_exclude(text, exclude_patterns)
        if excluded:
            continue

        # 构建 URL
        w_uid = w.get("user", {}).get("id") or uid
        mid   = w.get("mid") or w.get("mblogid", "")
        url   = f"https://weibo.com/{w_uid}/{mid}" if mid else ""

        items.append({
            "title":     text[:140] + ("…" if len(text) > 140 else ""),
            "url":       url,
            "published": pub,
            "entity":    name,
            "domain":    "weibo.com",
        })

    return items, None


def fetch_weibo_layer(weibo_cfg, hours, exclude_patterns):
    all_items    = []
    status_lines = []

    for acc in weibo_cfg:
        name = acc["name"]
        uid  = acc["uid"]
        items, err = fetch_weibo_account(name, uid, hours, exclude_patterns)
        if err:
            line = f"  ❌ {name} — {err}"
        else:
            line = f"  ✅ {name} — 保留{len(items)}条"
            all_items.extend(items)
        print(line)
        status_lines.append(line)

    return all_items, status_lines


# ── 去重 ──────────────────────────────────────────────────────────────────────
def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        key = item["url"] or item["title"]
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


# ── 排序 ──────────────────────────────────────────────────────────────────────
def sort_items(items):
    def key(i):
        p = i.get("published")
        if p is None:
            return datetime.min.replace(tzinfo=timezone.utc)
        return p
    return sorted(items, key=key, reverse=True)


# ── 输出 Markdown ─────────────────────────────────────────────────────────────
def render_items(items):
    if not items:
        return "_（无内容）_\n"
    lines = []
    for item in items:
        ago   = time_ago(item.get("published"))
        title = item["title"].replace("\n", " ").strip()
        url   = item["url"]
        entity = item["entity"]
        if url:
            lines.append(f"- [{title}]({url})  \n  `{entity}` · {ago}")
        else:
            lines.append(f"- {title}  \n  `{entity}` · {ago}")
    return "\n".join(lines) + "\n"


def write_report(official_items, media_items, x_items, weibo_items,
                 official_status, media_status, x_status, weibo_status,
                 hours, run_time):
    date_str = run_time.strftime("%Y-%m-%d")
    time_str = run_time.strftime("%H:%M")
    filename = OUTPUT_DIR / f"{date_str}.md"

    lines = []
    lines.append(f"# 科技资讯采集报告 · {date_str}")
    lines.append(f"> 采集时间：{time_str} CST　｜　时间窗口：过去 {hours} 小时\n")

    # ── 第一层：官方信源 ──────────────────────────────────────
    lines.append("---\n")
    lines.append(f"## 🔵 官方信源（{len(official_items)} 条）\n")
    lines.append(render_items(sort_items(official_items)))

    # ── 第二层：英文媒体 ──────────────────────────────────────
    lines.append("---\n")
    lines.append(f"## 🟠 英文媒体（{len(media_items)} 条）\n")
    lines.append(render_items(sort_items(media_items)))

    # ── 第三层：X ─────────────────────────────────────────────
    lines.append("---\n")
    lines.append(f"## 🐦 X / Twitter（{len(x_items)} 条）\n")
    lines.append(render_items(sort_items(x_items)))

    # ── 第四层：微博 ──────────────────────────────────────────
    lines.append("---\n")
    lines.append(f"## 🟡 微博（{len(weibo_items)} 条）\n")
    lines.append(render_items(sort_items(weibo_items)))

    # ── 采集状态摘要 ──────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 📊 采集状态\n")
    lines.append("### 官方信源")
    lines.append("\n".join(official_status) or "_无_")
    lines.append("\n### 英文媒体")
    lines.append("\n".join(media_status) or "_无_")
    lines.append("\n### X / Twitter")
    lines.append("\n".join(x_status) or "_跳过_")
    lines.append("\n### 微博")
    lines.append("\n".join(weibo_status) or "_跳过_")

    content = "\n".join(lines)
    filename.write_text(content, encoding="utf-8")
    return filename


# ── 主流程 ────────────────────────────────────────────────────────────────────
def flatten_official_sources(cfg):
    """把 official 下的所有子分组拍平成一个列表。"""
    sources = []
    for group_sources in cfg["official"].values():
        sources.extend(group_sources)
    return sources


def main():
    parser = argparse.ArgumentParser(description="科技资讯日报采集脚本")
    parser.add_argument("--skip-x",     action="store_true", help="跳过 X 采集")
    parser.add_argument("--skip-weibo", action="store_true", help="跳过微博采集")
    parser.add_argument("--hours",      type=int, default=48, help="时间窗口（小时），默认48")
    args = parser.parse_args()

    run_time = now_cst()
    print(f"\n{'='*60}")
    print(f"  科技资讯采集  {run_time.strftime('%Y-%m-%d %H:%M')} CST")
    print(f"  时间窗口：过去 {args.hours} 小时")
    print(f"{'='*60}\n")

    cfg     = load_yaml(SOURCES)
    filters = load_yaml(FILTERS)
    exclude_patterns = build_exclude_patterns(filters)

    # ── 第一层：官方信源 ──────────────────────────────────────
    print("🔵 采集官方信源…")
    official_sources = flatten_official_sources(cfg)
    official_items, official_status = fetch_layer(
        official_sources, args.hours, exclude_patterns, "官方"
    )
    official_items = deduplicate(official_items)
    print(f"   完成：{len(official_items)} 条\n")

    # ── 第二层：英文媒体 ──────────────────────────────────────
    print("🟠 采集英文媒体…")
    media_items, media_status = fetch_layer(
        cfg["media"], args.hours, exclude_patterns, "媒体"
    )
    media_items = deduplicate(media_items)
    print(f"   完成：{len(media_items)} 条\n")

    # ── 第三层：X ─────────────────────────────────────────────
    x_items   = []
    x_status  = []
    if args.skip_x:
        print("🐦 X 采集已跳过（--skip-x）\n")
        x_status = ["  ⏭️ 手动跳过"]
    else:
        print("🐦 采集 X / Twitter…")
        x_items, x_status = fetch_x_layer(
            cfg["x_accounts"], args.hours, exclude_patterns
        )
        x_items = deduplicate(x_items)
        print(f"   完成：{len(x_items)} 条\n")

    # ── 第四层：微博 ──────────────────────────────────────────
    weibo_items  = []
    weibo_status = []
    if args.skip_weibo:
        print("🟡 微博采集已跳过（--skip-weibo）\n")
        weibo_status = ["  ⏭️ 手动跳过"]
    else:
        print("🟡 采集微博…")
        weibo_items, weibo_status = fetch_weibo_layer(
            cfg.get("weibo_accounts", []), args.hours, exclude_patterns
        )
        weibo_items = deduplicate(weibo_items)
        print(f"   完成：{len(weibo_items)} 条\n")

    # ── 写报告 ────────────────────────────────────────────────
    out_file = write_report(
        official_items, media_items, x_items, weibo_items,
        official_status, media_status, x_status, weibo_status,
        args.hours, run_time,
    )

    total = len(official_items) + len(media_items) + len(x_items) + len(weibo_items)
    print(f"{'='*60}")
    print(f"  ✅ 完成！共 {total} 条")
    print(f"     官方 {len(official_items)} 条  |  媒体 {len(media_items)} 条  |  X {len(x_items)} 条  |  微博 {len(weibo_items)} 条")
    print(f"  📄 输出：{out_file}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
