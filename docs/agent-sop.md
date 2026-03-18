# 科技资讯日报 Agent 标准操作程序（SOP）

> 版本：v1.0  
> 用途：指导 AI Agent 完成每日科技资讯采集、筛选、分类、整理全流程

---

## 第一阶段：采集（四级漏斗）

### L0：X/Twitter 采集（硬性阻断点）

**命令**：
```bash
export PATH="/Users/yangliu/.local/bin:$PATH"

# 获取关注时间线（优先）
twitter feed -t following --max 50 --yaml

# 备选：获取推荐时间线
twitter feed --max 50 --yaml
```

**提取字段**：
- `text` - 推文内容
- `author.screenName` - 发布者
- `createdAtLocal` - 时间
- `metrics.likes` / `metrics.retweets` - 互动数据

**筛选规则**：
- 只保留 24h 内的推文
- 过滤转发（`isRetweet: true` 的丢弃）
- 互动数 ≥ 50 或发布者为 Tier 1 账号的保留

**失败处理**：
- 如果返回 `authenticated: false` → 停止整个流程，报告 Cookie 过期
- 如果请求超时 → 等待 60 秒后重试，最多 3 次
- **绝对禁止跳过 L0 直接执行 L1**

---

### L0.5：微博采集

**命令**：
```bash
cd /Users/yangliu/Documents/Claude\ Code/codebuddy/tech-daily-brief
python3 scripts/weibo_fetch.py --max 10
```

**筛选规则**：
- 只保留 24h 内的微博
- 原创优先（转发数 > 评论数的可能是热点）

---

### L1：聚合搜索（按板块执行）

**读取关键词配置**：
```yaml
# config/search_keywords.yaml
# 按 6 个板块逐个搜索，每板块 2-3 组关键词
```

**执行顺序**：
1. **global**（通用热点）→ Tavily 搜索 "AI news today"
2. **ai_models** → 搜索 OpenAI/Anthropic/Google 动态
3. **mobile** → 搜索 Apple/Samsung/小米 动态
4. **chips** → 搜索 NVIDIA/AMD/台积电 动态
5. **gaming** → 搜索 Steam/PS5/Xbox 动态
6. **tech_industry** → 搜索融资/并购/财报
7. **policy** → 搜索 AI 法规/监管

**工具分配**：
| 场景 | 工具 | 命令示例 |
|------|------|----------|
| 英文综合 | Tavily | `tavily_search "OpenAI GPT-5 release" max_results=10` |
| 中文搜索 | web_search | `web_search "OpenAI GPT-5 发布"` |
| 聚合站扫描 | web_fetch | 抓取 36氪/虎嗅首页 |

**去重规则**：
- 同一事件只保留最早的信源
- 标题相似度 > 80% 视为同一事件

---

### L2：观点聚合

**目的**：为重点话题收集多方观点，支撑洞察写作

**操作**：
1. 打开 https://xclaw.info/zh/tweets?group=global&tag=ai
2. 搜索候选新闻的关键词
3. 记录 2-3 个权威观点（带 @用户名）

---

### L3：深度抓取

**必须抓取全文的新闻**：
- 官方产品发布（GPT-5、Claude 新版等）
- 财报/重大合作/并购
- 政策法规变动

**抓取工具优先级**：
1. Jina Reader：`curl -s "https://r.jina.ai/URL"`
2. Tavily Extract：`tavily_extract urls=["URL"]`
3. web_fetch：内置工具

**数量要求**：每期至少 3-5 篇全文

---

## 第二阶段：筛选（从 30-50 条到 18-22 条）

### 筛选漏斗

```
原始采集：30-50 条
    ↓ 删除过时（>48h）：-5~10 条
    ↓ 删除低质量信源（Tier 4 单源）：-5~8 条
    ↓ 删除重复事件：-3~5 条
    ↓ 删除过于小众：-2~3 条
候选池：18-22 条
```

### 质量评分标准

| 维度 | 评分 | 说明 |
|------|------|------|
| 时效性 | 0-3 | 24h 内=3，24-48h=2，>48h=0（删除） |
| 信源层级 | 0-3 | Tier 1=3，Tier 2=2，Tier 3=1，Tier 4=0 |
| 重要性 | 0-3 | 行业重大=3，公司重要=2，常规更新=1 |
| 独家性 | 0-1 | 首发/独家=1，否则=0 |

**保留规则**：总分 ≥ 5 分的保留

---

## 第三阶段：分类（6 大板块）

### 分类规则

| 板块 | 判定标准 | 数量目标 |
|------|----------|----------|
| 🧠 AI 模型与产品 | 大模型发布、产品更新、技术突破 | 3-4 条 |
| 📱 手机与消费电子 | 手机厂商、硬件发布、可穿戴设备 | 3-4 条 |
| 🔧 芯片与算力 | GPU/CPU 发布、代工动态、算力基建 | 2-3 条 |
| 🎮 游戏行业 | 平台政策、游戏发售、行业活动 | 2-3 条 |
| 🏛️ 科技行业动态 | 财报、融资、并购、人事变动 | 2-3 条 |
| 📜 政策与监管 | AI 法规、反垄断、出口管制 | 1-2 条 |

### 冲突处理

- 同一公司多条新闻 → 选最重要的一条，其他合并简述
- 跨板块新闻 → 选最相关的板块，不重复放置
- 板块数量不足 → 从候选池补充，或降低该板块数量

---

## 第四阶段：整理（生成日报）

### 读取模板

```bash
# 必须读取 template.html
cat template.html
```

**模板占位符**：
- `{{DATE}}` - 日期
- `{{SUMMARY}}` - 核心要闻（5-6 条一句话总结）
- `{{SECTIONS}}` - 6 大板块内容

### 单条新闻格式

```html
<div class="item">
  <div class="item-title">
    <span class="tag tag-new">新品</span>
    [标题：公司+动作+关键数据]
  </div>
  <div class="item-body">
    [正文：时间+核心事实+关键数据，100-150字]
  </div>
  <div class="stat-row">
    <span class="stat">维度1 <em>数值1</em></span>
    <span class="stat">维度2 <em>数值2</em></span>
  </div>
  <div class="item-source">
    来源：[信源名称](URL) ｜ [信源名称](URL) ｜ 日期
  </div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">
      [200-300字独立观点，禁止仅凭摘要写]
      [必须基于：全文内容 + XClaw 观点搜索 + 权威观点]
      [角度：定价策略/技术路线/行业影响/竞争格局]
    </div>
  </div>
</div>
```

### 洞察写作检查清单

```
□ 是否阅读了全文？（不是只看标题/摘要）
□ 是否搜索了 X 上的讨论？（XClaw 或手动搜索）
□ 是否有权威观点支撑？（@用户名引用）
□ 是否提供了独特视角？（不是重复正文）
□ 字数是否在 200-300 字之间？
```

---

## 第五阶段：发布

### 文件输出

```bash
# 保存到 brief/YYYY-MM-DD.html
# YYYY-MM-DD 为当天日期
```

### 三端同步

| 渠道 | 操作 | 检查点 |
|------|------|--------|
| 网页 | git push | index.html 已更新 |
| 邮件 | python scripts/send_email.py | 8 位收件人收到 |
| 公众号 | node publish-daily.mjs | 草稿箱有内容 |

---

## 附录：信源层级速查

### Tier 1（⭐⭐⭐⭐⭐ 可直接引用）
- AI 公司官方：OpenAI、DeepMind、Anthropic、Meta AI、xAI
- 关键人物：@sama、@elonmusk、@demishassabis、@karpathy、@DrJimFan
- 数据平台：SteamDB、Famitsu、Circana

### Tier 2（⭐⭐⭐⭐ 可引用，关键数据需交叉验证）
- 国际媒体：TechCrunch、The Verge、Wired、Ars Technica
- 中文媒体：机器之心、量子位、新智元

### Tier 3（⭐⭐⭐ 需二次确认）
- 社区：HackerNews、Reddit、GitHub Trending
- 投资：红杉、Konvoy

### Tier 4（⭐⭐ 仅作线索）
- 聚合站：36氪、虎嗅、Buzzing

---

## 故障处理

| 问题 | 解决方案 |
|------|----------|
| twitter-cli 失败 | 停止流程，报告 Cookie 过期 |
| Tavily 限流 | 切换到 web_search |
| Jina Reader 失败 | 使用 tavily_extract |
| 某板块新闻不足 | 降低该板块数量，不硬凑 |
| 洞察写不出来 | 重新抓取全文，搜索 X 讨论 |

---

## 输出示例

见 `brief/2026-03-17.html`
