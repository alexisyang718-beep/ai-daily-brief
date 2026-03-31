#!/usr/bin/env python3
"""
选题报告生成器（统一版）

功能：
1. 读取当日采集的 Atom 数据（x.jsonl / weibo.jsonl / rss.jsonl）
2. 预处理：去重、时效过滤（48h）、信源打标
3. 按6大模块分类，每模块按评分排序
4. 输出精选 25-30 条选题报告（Markdown 格式）
5. 包含：✅ 入选标记、来源、URL、核心内容、入选理由、统计表

输出：v2/docs/daily_selection_YYYYMMDD.md

使用方式：
    # 默认今天
    python3 generate_selection_report.py

    # 指定日期
    python3 generate_selection_report.py --date 2026-03-30

    # 合并多天数据（如昨天+今天）
    python3 generate_selection_report.py --date 2026-03-30 --include-prev

    # 全量模式（输出所有条目，不精选）
    python3 generate_selection_report.py --date 2026-03-30 --full

    # 定时刷新
    python3 generate_selection_report.py --watch --interval 300
"""

import json
import time
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# 添加 v2/scripts 到 path
sys.path.insert(0, str(Path(__file__).parent))
from atom_store import AtomStore

# ============ 路径 ============
V2_ROOT = Path(__file__).parent.parent
DOCS_DIR = V2_ROOT / "docs"

# ============ 6大模块（严格只有这6个） ============
MODULES = {
    "ai_models":      {"name": "🤖AI模型与产品",   "icon": "🤖", "target": 6, "priority": 0},
    "mobile":         {"name": "📱手机与消费电子",  "icon": "📱", "target": 5, "priority": 0},
    "chips":          {"name": "🔧芯片与算力",      "icon": "🔧", "target": 5, "priority": 0},
    "gaming":         {"name": "🎮游戏行业",        "icon": "🎮", "target": 4, "priority": 1},
    "tech_industry":  {"name": "🏢科技行业动态",    "icon": "🏢", "target": 5, "priority": 1},
    "policy":         {"name": "📜政策与监管",       "icon": "📜", "target": 4, "priority": 1},
}
MODULE_ORDER = ["ai_models", "mobile", "chips", "gaming", "tech_industry", "policy"]

# ============ 信源分级 ============
OFFICIAL_ACCOUNTS = {
    # X 官方账号
    "@openai", "@anthropicai", "@googledeepmind", "@googleai", "@nvidia",
    "@metaai", "@xai", "@microsoft", "@apple", "@deepseek_ai",
    "@mistralai", "@huggingface", "@stability_ai", "@perplexity_ai",
    "@runwayml", "@midjourney", "@cursor_ai", "@github",
    # X CEO/高管
    "@sama", "@elonmusk", "@demishassabis", "@satyanadella", "@ylecun",
    "@karpathy", "@darioamodei", "@drjimfan",
}

TIER1_MEDIA_DOMAINS = {
    "bloomberg.com", "reuters.com", "9to5mac.com", "appleinsider.com",
    "9to5google.com", "sammobile.com", "samsungnewsroom.com",
}

TIER2_MEDIA_DOMAINS = {
    "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
    "technologyreview.com", "venturebeat.com",
    "36kr.com", "huxiu.com", "ifanr.com", "jiqizhixin.com",
    "gamesindustry.biz", "eurogamer.net", "pcgamer.com",
}

TIER2_WEIBO_AUTHORS = {
    "机器之心pro", "机器之心", "量子位", "新智元", "财联社app",
    "36氪", "虎嗅app", "竞核", "梁赛",
}

# ============ 排除规则 ============
EXCLUDE_KEYWORDS = [
    "抽奖", "转发抽奖", "福利", "免费送", "优惠券", "直播间",
    "减肥药", "诺和诺德", "橄榄球", "足球赛事", "石油公司",
]

# ============ 内容类型标签 ============
CONTENT_TYPE_LABELS = {
    "official": "官方", "exclusive": "独家", "firsthand_test": "实测",
    "original_analysis": "分析", "report": "报道", "interview": "采访",
    "commentary": "评论", "translation": "编译", "repost": "转发",
}

PLATFORM_ICONS = {"x": "𝕏", "weibo": "📡", "rss": "📰", "web": "🌐"}


def normalize_url(url: str) -> str:
    """规范化 URL 用于去重"""
    if not url:
        return ""
    url = url.rstrip("/")
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        cleaned = {k: v for k, v in params.items()
                   if not k.startswith("utm_") and k not in ("ref", "source", "from")}
        return urlunparse(parsed._replace(query=urlencode(cleaned, doseq=True)))
    except Exception:
        return url


def get_source_label(atom: Dict) -> Tuple[int, str]:
    """
    判断信源级别：(tier_num, label_text)
    1 = 一手官方, 2 = 一手媒体, 3 = 二手编译
    """
    source = atom.get("source", {})
    author = source.get("author", "").lower().strip()
    url = source.get("url", "")
    author_type = source.get("author_type", "")

    # 官方/CEO/研究员
    if author_type in ("official", "ceo_cto", "researcher", "expert_kol"):
        return (1, "一手官方")
    if author in OFFICIAL_ACCOUNTS or f"@{author.lstrip('@')}" in OFFICIAL_ACCOUNTS:
        return (1, "一手官方")

    # 权威媒体
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        domain = ""
    if domain and any(d in domain for d in TIER1_MEDIA_DOMAINS):
        return (2, "一手媒体")
    if domain and any(d in domain for d in TIER2_MEDIA_DOMAINS):
        return (2, "一手媒体")
    if author.lower().strip() in TIER2_WEIBO_AUTHORS:
        return (2, "中文媒体")
    if author_type == "media":
        return (2, "一手媒体")

    return (3, "二手/社区")


def score_atom(atom: Dict) -> float:
    """
    综合评分：信源质量 × 内容类型 × 互动数据 × 渠道加权
    用于排序，分数越高越好
    """
    score = 0.0

    # 信源质量
    trust = atom.get("trust_default", "L3")
    score += {"L1": 100, "L2": 60, "L3": 20}.get(trust, 10)

    # 内容类型
    ct = atom.get("content_type", "commentary")
    score += {
        "official": 50, "exclusive": 45, "firsthand_test": 40,
        "original_analysis": 30, "report": 25, "interview": 20,
        "commentary": 10, "translation": 5, "repost": 0,
    }.get(ct, 5)

    # 互动数据（X/微博）
    metrics = atom.get("metrics", {})
    if metrics:
        likes = metrics.get("likes", 0) or 0
        retweets = metrics.get("retweets", 0) or 0
        replies = metrics.get("replies", 0) or 0
        engagement = likes + retweets * 2 + replies * 3
        if engagement > 0:
            import math
            score += min(math.log1p(engagement) * 5, 50)  # 最多加50分

    # RSS 渠道加权（RSS 无互动数据，需要补偿）
    platform = atom.get("source", {}).get("platform", "")
    source_tier = atom.get("_source_tier", 3)
    if platform == "rss":
        # RSS 一手内容（T1/T2）额外加分，确保能与微博互动数据竞争
        if source_tier == 1:
            score += 60  # 官方博客内容
        elif source_tier == 2:
            score += 40  # 媒体内容
    
    # X 渠道加权（X 英文内容缺乏中文关键词匹配，需要补偿）
    if platform == "x":
        author = atom.get("source", {}).get("author", "").lower().strip()
        # T1 官方账号（OpenAI/Anthropic/NVIDIA 等）
        T1_X_AUTHORS = {
            "@openai", "@anthropicai", "@googledeepmind", "@googleai", "@meta", "@metaai",
            "@nvidia", "@xai", "@microsoft", "@microsoftai", "@apple", "@stability_ai",
            "@huggingface", "@deepseek_ai", "@mistralai", "@perplexity_ai",
            "@midjourney", "@runwayml", "@cursor_ai", "@github", "@vercel", "@cloudflare",
            "@google", "@amazon", "@aws", "@azure", "@spaceX",
        }
        # CEO/CTO/研究员
        CEO_CTO_AUTHORS = {
            "@sama", "@elonmusk", "@demishassabis", "@ylecun", "@karpathy",
            "@drjimfan", "@darioamodei", "@satyanadella", "@jasonwei20",
            "@arthurmensch", "@clementdelangue", "@gdb", "@ilyasut",
            "@geoffreyhinton", "@fchollet",
        }
        # T2 科技媒体
        T2_X_AUTHORS = {
            "@techcrunch", "@verge", "@wired", "@theinformation", "@semianalysis",
            "@huggingface", "@simonw", "@lilianweng", "@jeremyphoward",
        }
        
        if author in T1_X_AUTHORS or author in CEO_CTO_AUTHORS:
            score += 80  # 官方/CEO 一手信源，最高权重
        elif author in T2_X_AUTHORS:
            score += 50  # 科技媒体/博客
        elif source_tier == 2:
            score += 30  # 其他媒体源

    # 实体丰富度
    entities = atom.get("entities", [])
    score += min(len(entities) * 3, 15)

    # 短内容降权（< 100 字符的 X/微博内容，通常是低信息量推文）
    title = atom.get("title", "")
    summary = atom.get("summary_zh", "") or ""
    content_len = len(title) + len(summary)
    if platform in ("x", "weibo") and content_len < 100:
        score -= 30  # 短内容大幅降权

    return score


def is_excluded(atom: Dict) -> bool:
    """检查是否应排除"""
    text = (atom.get("title", "") + atom.get("summary_zh", "")).lower()
    return any(kw in text for kw in EXCLUDE_KEYWORDS)


def check_freshness(atom: Dict, max_hours: int = 48) -> bool:
    """检查时效性（基于 source.timestamp）"""
    ts = atom.get("source", {}).get("timestamp", "")
    if not ts:
        return True  # 无时间戳的不过滤（可能是 RSS 没解析到时间）

    from email.utils import parsedate_to_datetime as _parse_rfc
    now = datetime.now()

    for parser in [
        lambda s: _parse_rfc(s),
        lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")),
        lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M"),
        lambda s: datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y"),
    ]:
        try:
            dt = parser(ts)
            if hasattr(dt, 'tzinfo') and dt.tzinfo:
                dt = dt.replace(tzinfo=None)  # 简化比较
            return (now - dt).total_seconds() < max_hours * 3600
        except Exception:
            continue
    return True  # 解析失败不过滤


class SelectionReportGenerator:
    """选题报告生成器"""

    def __init__(self, date: str = None, include_prev: bool = False, full_mode: bool = False):
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.include_prev = include_prev
        self.full_mode = full_mode
        self.store = AtomStore()

    def load_atoms(self) -> List[Dict]:
        """加载数据（支持合并前一天）"""
        atoms = self.store.query_by_date(self.date)
        if self.include_prev:
            prev_date = (datetime.strptime(self.date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            prev_atoms = self.store.query_by_date(prev_date)
            atoms.extend(prev_atoms)
        return atoms

    def preprocess(self, atoms: List[Dict]) -> List[Dict]:
        """预处理：去重 + 排除 + 时效过滤 + 信源打标 + 评分"""
        # 1. URL 去重
        seen_urls = set()
        unique = []
        for atom in atoms:
            url = normalize_url(atom.get("source", {}).get("url", ""))
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            unique.append(atom)

        # 2. 排除不感兴趣内容
        unique = [a for a in unique if not is_excluded(a)]

        # 3. 时效过滤（48h）
        unique = [a for a in unique if check_freshness(a, 48)]

        # 4. 信源打标 + 评分
        for atom in unique:
            tier, label = get_source_label(atom)
            atom["_source_tier"] = tier
            atom["_source_label"] = label
            atom["_score"] = score_atom(atom)

        # 5. 规范分类（只保留6大模块）
        valid_cats = set(MODULE_ORDER)
        for atom in unique:
            cat = atom.get("category", "tech_industry")
            if cat not in valid_cats:
                atom["category"] = "tech_industry"

        return unique

    def select_top(self, atoms: List[Dict]) -> Dict[str, List[Dict]]:
        """按模块精选 top N 条"""
        # 按模块分组
        by_module = defaultdict(list)
        for atom in atoms:
            by_module[atom.get("category", "tech_industry")].append(atom)

        # 每个模块按评分排序，取 target 条
        selected = {}
        for mod_key in MODULE_ORDER:
            mod_atoms = by_module.get(mod_key, [])
            mod_atoms.sort(key=lambda a: a.get("_score", 0), reverse=True)
            target = MODULES[mod_key]["target"]

            if self.full_mode:
                selected[mod_key] = mod_atoms
            else:
                selected[mod_key] = mod_atoms[:target]

        return selected

    def generate_reason(self, atom: Dict) -> str:
        """生成入选理由（基于评分因子）"""
        parts = []
        trust = atom.get("trust_default", "L3")
        ct = atom.get("content_type", "")
        label = atom.get("_source_label", "")
        entities = atom.get("entities", [])

        if trust == "L1":
            parts.append("官方/权威一手信源")
        elif trust == "L2":
            parts.append(f"{label}来源")

        ct_label = CONTENT_TYPE_LABELS.get(ct, "")
        if ct_label and ct in ("official", "exclusive", "firsthand_test"):
            parts.append(f"{ct_label}内容")

        if entities:
            parts.append(f"涉及{'、'.join(entities[:3])}")

        metrics = atom.get("metrics", {})
        likes = metrics.get("likes", 0) or 0
        if likes > 100:
            parts.append(f"高互动({likes}❤️)")

        return "；".join(parts) if parts else "相关度高"

    def format_stats_table(self, selected: Dict[str, List[Dict]], total_raw: int) -> str:
        """生成统计表"""
        lines = []
        lines.append("## 选题统计\n")
        lines.append("| 模块 | 入选 | X | 微博 | RSS | 备注 |")
        lines.append("|------|------|---|------|-----|------|")

        total_selected = 0
        for mod_key in MODULE_ORDER:
            mod_atoms = selected.get(mod_key, [])
            mod_name = MODULES[mod_key]["name"]
            x_count = sum(1 for a in mod_atoms if a.get("source", {}).get("platform") == "x")
            wb_count = sum(1 for a in mod_atoms if a.get("source", {}).get("platform") == "weibo")
            rss_count = sum(1 for a in mod_atoms if a.get("source", {}).get("platform") == "rss")
            # 提取主要实体作为备注
            all_entities = []
            for a in mod_atoms[:3]:
                all_entities.extend(a.get("entities", [])[:2])
            note = "、".join(dict.fromkeys(all_entities))[:30]  # 去重+限长
            lines.append(f"| {mod_name} | {len(mod_atoms)}条 | {x_count} | {wb_count} | {rss_count} | {note} |")
            total_selected += len(mod_atoms)

        lines.append(f"| **合计** | **{total_selected}条** | | | | 候选池{total_raw}条 |")
        return "\n".join(lines)

    def format_atom(self, atom: Dict, idx: int, is_selected: bool) -> str:
        """格式化单条选题"""
        lines = []
        source = atom.get("source", {})
        platform = source.get("platform", "")
        author = source.get("author", "未知")
        url = source.get("url", "")
        trust = atom.get("trust_default", "L3")
        ct = atom.get("content_type", "")
        ct_label = CONTENT_TYPE_LABELS.get(ct, ct)

        # 标题
        title = atom.get("title_zh") or atom.get("title", "无标题")
        title_clean = title.strip().replace("\n", " ")[:120]
        prefix = "✅" if is_selected else "⚠️"

        lines.append(f"### {prefix} {idx}. {title_clean}")

        # 来源行
        platform_icon = PLATFORM_ICONS.get(platform, "📄")
        lines.append(f"- **来源**: {author} ({platform_icon} {platform}) [{ct_label}]")

        # URL
        if url:
            lines.append(f"- **URL**: {url}")

        # 核心内容
        summary = atom.get("summary_zh", "")
        if summary:
            summary_clean = summary.strip().replace("\n", " ")[:250]
            lines.append(f"- **核心内容**: {summary_clean}")

        # 入选理由（仅入选条目）
        if is_selected:
            reason = self.generate_reason(atom)
            lines.append(f"- **入选理由**: {reason}")

        lines.append("")
        return "\n".join(lines)

    def generate_report(self) -> str:
        """生成完整选题报告"""
        # 1. 加载数据
        raw_atoms = self.load_atoms()
        if not raw_atoms:
            return f"# 选题报告 - {self.date}\n\n暂无数据。请先运行采集。\n"

        # 2. 预处理
        atoms = self.preprocess(raw_atoms)

        # 3. 精选
        selected = self.select_top(atoms)

        # 4. 生成报告
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        total_selected = sum(len(v) for v in selected.values())

        lines = []
        lines.append(f"# 选题报告 - {self.date}日报\n")
        lines.append(f"> 生成时间: {now}")
        lines.append(f"> 数据来源: X + 微博 + RSS{'（含前一天数据）' if self.include_prev else ''}")
        lines.append(f"> 候选池: {len(atoms)}条 → 精选{total_selected}条")
        lines.append(f"> 规则: 每模块前{MODULES['ai_models']['target']}条 ✅ 标记为日报入选，其余为备选")
        lines.append("")
        lines.append("---\n")

        # 统计表
        lines.append(self.format_stats_table(selected, len(atoms)))
        lines.append("\n---\n")

        # 各模块详情
        for mod_key in MODULE_ORDER:
            mod_atoms = selected.get(mod_key, [])
            mod_name = MODULES[mod_key]["name"]
            target = MODULES[mod_key]["target"]

            # 模块标题
            by_module_all = [a for a in atoms if a.get("category") == mod_key]
            lines.append(f"## {mod_name} ({len(mod_atoms)}条精选 / {len(by_module_all)}条候选)\n")

            for i, atom in enumerate(mod_atoms, 1):
                is_top = i <= target  # 前 target 条标 ✅
                lines.append(self.format_atom(atom, i, is_top))

            lines.append("---\n")

        # 底部：今日三大头条建议
        all_selected = []
        for mod_key in MODULE_ORDER:
            for a in selected.get(mod_key, []):
                all_selected.append(a)
        all_selected.sort(key=lambda a: a.get("_score", 0), reverse=True)

        if all_selected[:3]:
            lines.append("## 📌 今日三大头条建议\n")
            for i, atom in enumerate(all_selected[:3], 1):
                title = (atom.get("title_zh") or atom.get("title", ""))[:80]
                mod = MODULES.get(atom.get("category", ""), {}).get("name", "")
                lines.append(f"❶❷❸"[i-1] + f" **{title}** [{mod}]")
            lines.append("")

        # 底部附注
        lines.append("---\n")
        lines.append(f"*生成时间: {now} | 数据源: v2/archive/daily/{self.date}/ | 偏好配置: workflow/02-selection/news-preferences.md*")

        return "\n".join(lines)

    def save_report(self) -> Path:
        """保存报告"""
        report = self.generate_report()
        date_compact = self.date.replace("-", "")
        report_path = DOCS_DIR / f"daily_selection_{date_compact}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return report_path

    def watch_mode(self, interval: int = 300):
        """定时刷新模式"""
        print(f"👀 启动定时刷新（每 {interval} 秒）")
        try:
            while True:
                path = self.save_report()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 已更新: {path}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 已停止")


def main():
    parser = argparse.ArgumentParser(description="选题报告生成器")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="日期 (YYYY-MM-DD，默认今天)")
    parser.add_argument("--include-prev", action="store_true",
                        help="合并前一天数据")
    parser.add_argument("--full", action="store_true",
                        help="全量模式（不精选，输出所有条目）")
    parser.add_argument("--watch", action="store_true",
                        help="定时刷新模式")
    parser.add_argument("--interval", type=int, default=300,
                        help="刷新间隔秒数（默认300）")

    args = parser.parse_args()

    gen = SelectionReportGenerator(
        date=args.date,
        include_prev=args.include_prev,
        full_mode=args.full,
    )

    if args.watch:
        gen.watch_mode(interval=args.interval)
    else:
        path = gen.save_report()
        atoms = gen.preprocess(gen.load_atoms())
        selected = gen.select_top(atoms)
        total = sum(len(v) for v in selected.values())

        print(f"✅ 选题报告已生成: {path}")
        print(f"📊 候选 {len(atoms)} 条 → 精选 {total} 条\n")
        for mod_key in MODULE_ORDER:
            mod_atoms = selected.get(mod_key, [])
            mod_name = MODULES[mod_key]["name"]
            print(f"  {mod_name}: {len(mod_atoms)} 条")


if __name__ == "__main__":
    main()
