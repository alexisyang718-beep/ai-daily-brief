#!/usr/bin/env python3
"""
生成科技资讯日报 HTML - 2026年3月17日版
"""
from datetime import datetime

with open('template.html', 'r', encoding='utf-8') as f:
    template = f.read()

today = datetime.now()
date_cn = f"{today.year}年{today.month}月{today.day}日"
weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]
date_title = f"{today.month}月{today.day}日"

template = template.replace('{{DATE_TITLE}}', date_title)
template = template.replace('{{DATE_CN}}', date_cn)
template = template.replace('{{WEEKDAY}}', weekday)

summary = """
❶ <strong>NVIDIA GTC 2026</strong> 发布 Vera Rubin 平台：3nm 工艺 3360 亿晶体管，2027 年订单目标 <strong>1万亿美元</strong>（翻倍）<br>
❷ <strong>阿里成立 ATH 事业群</strong>：CEO 吴泳铭挂帅，"创造/输送/应用 Token"为核心目标<br>
❸ <strong>Google Play</strong> 推出 Gemini Live AI 助手 + Game Trials 试玩 + 跨设备购买<br>
❹ <strong>陈天桥</strong> MiroMind 发布 MiroThinker-1.7，342次工具调用刷新 SOTA<br>
❺ <strong>国产手机</strong> 4月新机：小米 16 6.36" 8000mAh、Find X9 Ultra 6.9英寸 2nm<br>
❻ <strong>苹果</strong> 发布 AirPods Max 2：H2 芯片、降噪提升 1.5 倍、3999 元
"""
template = template.replace('{{SUMMARY}}', summary)

template = template.replace('{{COVERAGE_RANGE}}', '24小时（X/Twitter + 微博 + 国内外科技媒体）')
template = template.replace('{{SOURCES_LIST}}', '<strong>Twitter/X</strong>、微博 @数码闲聊站、IT之家、36kr、量子位、新浪财经')

# ==================== 1. AI 模型与产品 ====================
model_items = """
<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    陈天桥 MiroMind 发布 MiroThinker-1.7：霸榜多项深度推理测试
  </div>
  <div class="item-body">
    陈天桥创办的 <strong>MiroMind</strong> 发布新一代重型推理智能体 <strong>MiroThinker-1.7</strong> 和 MiroThinker-H1。MiroThinker-H1 刷新 SOTA，超越 Gemini-3.1-Pro、GPT-5.4-Thinking、Claude-4.6-Opus 等闭源模型。<br><br>
    该模型在复杂推理任务中保持长达三分钟的"思考"状态，后台完成 <strong>342 次工具调用</strong>。同时开源模型 MiroThinker-1.7 (235B) 和 mini 版 (30B) 也已发布。
  </div>
  <div class="stat-row">
    <span class="stat">🧠 <em>深度推理</em></span>
    <span class="stat">🏆 <em>SOTA</em></span>
    <span class="stat">🔧 <em>342次调用</em></span>
  </div>
  <div class="item-source">来源：<a href="https://www.sohu.com/a/997299740_121124377" target="_blank">搜狐</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">陈天桥的 MiroMind 再次证明<strong>深度推理是当前大模型竞争的核心战场</strong>。342次工具调用意味着模型能够自主规划多步任务，这正是"Agent能力"的体现。MiroThinker-H1 超越 Claude-4.6-Opus——Anthropic 的旗舰模型，这对中国 AI 公司而言是重要突破。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-blue">🔧技术</span>
    Kimi 发布 attnres 论文：探索注意力机制新突破
  </div>
  <div class="item-body">
    月之暗面（Moonshot AI）发布 Kimi <strong>attnres</strong>（Attention Residuals）论文，谷歌高级 AI 产品经理 Shubham Saboo 评价称"<strong>他们触碰了那个十年没人敢碰的部分</strong>"。<br><br>
    该研究解决了 Transformer 架构中的一个十年痼疾，性能炸裂，相当于免费获得 1.25 倍算力。同时 Kimi K2.5 技术报告也已发布，开启"视觉智能体"新纪元，是业界首个原生多模态万亿参数模型。
  </div>
  <div class="stat-row">
    <span class="stat">📄 <em>attnres</em></span>
    <span class="stat">👁️ <em>视觉智能体</em></span>
    <span class="stat">🔢 <em>万亿参数</em></span>
    <span class="stat">⚡ <em>+125%算力</em></span>
  </div>
  <div class="item-source">来源：<a href="https://www.sohu.com/a/997299740_121124377" target="_blank">搜狐</a>、<a href="https://llm-stats.com/blog/research/kimi-k2-5-launch" target="_blank">LLM Stats</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">月之暗面在 attnres 上的突破显示<strong>注意力机制仍有巨大优化空间</strong>。谷歌 AI 产品经理的"高赞"说明这是行业公认的重要突破。"免费 1.25 倍算力"意味着无需增加硬件就能提升性能。视觉智能体是 K2.5 的核心方向——从"文本理解"到"视觉行动"，这是 AI Agent 的关键跨越。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    Anthropic CEO 警告：AI 将在 2026/2027 年达到"天才国家"智能水平
  </div>
  <div class="item-body">
    Anthropic CEO <strong>达里奥·阿莫代伊</strong>在巴黎人工智能行动峰会上表示，AI 将达到相当于"一个天才国家"的智能水平。同时 Anthropic 推出经济指数追踪 AI 对劳动市场的影响。微软公开声援 Anthropic，成为首家在 Anthropic 与美国国防部供应链风险争端中站队的科技巨头。
  </div>
  <div class="stat-row">
    <span class="stat">🏛️ <em>AI 预言</em></span>
    <span class="stat">📊 <em>经济指数</em></span>
    <span class="stat">🤝 <em>微软声援</em></span>
  </div>
  <div class="item-source">来源：<a href="https://www.163.com/dy/article/JPSSB8T505568VTV.html" target="_blank">网易新闻</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">从"天才个人"到"天才国家"，Anthropic 对 AI 能力的预测正在加速。<strong>2026-2027 年是关键时间窗口</strong>——如果预测成真，这将深刻改变全球经济格局和劳动力市场。微软声援 Anthropic 不仅是商业考量，更说明 AI 安全的全球治理已经触及国家层面。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-blue">🔧技术</span>
    Mistral 发布首个开源 Lean 4 代码代理 Leanstral
  </div>
  <div class="item-body">
    Mistral 推出 <strong>Leanstral</strong>，这是首个开源的 Lean 4 代码代理，标志着 AI 在形式化数学证明和代码验证领域的重要突破。
  </div>
  <div class="stat-row">
    <span class="stat">🤖 <em>代码代理</em></span>
    <span class="stat">📐 <em>Lean 4</em></span>
    <span class="stat">🔬 <em>形式化证明</em></span>
  </div>
  <div class="item-source">来源：<a href="https://twitter.com/MistralDevs" target="_blank">@MistralDevs (Twitter)</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">Leanstral 的出现填补了<strong>AI 辅助数学证明的开源空白</strong>。不同于传统的代码生成，Lean 4 是一种证明助手语言，要求严格的逻辑推导。这意味着 AI 不仅能写代码，还能"证明"代码的正确性——这在安全关键系统中有巨大价值。</div>
  </div>
</div>
"""
template = template.replace('{{SECTION_MODEL_ITEMS}}', model_items)

# ==================== 2. 手机与消费电子 ====================
phone_items = """
<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    苹果发布 AirPods Max 2：H2 芯片、降噪提升 1.5 倍、3999 元
  </div>
  <div class="item-body">
    <strong>3 月 16 日，苹果正式发布 AirPods Max 2</strong>，售价 <strong>3999 元</strong>，3 月 25 日开启预售，4 月初正式发售。新品搭载 H2 芯片升级版，新增自适应通透模式与钛合金可调节头带。<br><br>
    主动降噪功能相比前代提升 <strong>1.5 倍</strong>，续航提升至 30 小时。外观与前代几乎一致，提供午夜、星光、橙、紫、蓝五色，重 386.2 克。通过 USB-C 线支持 24-bit/48kHz 无损音频。
  </div>
  <div class="stat-row">
    <span class="stat">🎧 <em>H2 芯片</em></span>
    <span class="stat">🔇 <em>降噪 1.5x</em></span>
    <span class="stat">🔋 <em>30 小时</em></span>
    <span class="stat">💰 <em>3999 元</em></span>
  </div>
  <div class="item-source">来源：<a href="https://www.donews.com/news/detail/8/6469182.html" target="_blank">DoNews</a>、<a href="https://finance.sina.com.cn/tech/roll/2026-03-16/doc-inhrezkn9784676.shtml" target="_blank">新浪科技</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>AirPods Max 2 是苹果音频产品的"最后一块拼图"</strong>。H2 芯片的加入补齐了自适应音频、对话感知等计算音频功能，降噪 1.5 倍提升是最大卖点。3999 元的价格维持不变，说明苹果在高端头戴耳机市场没有对手。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    Google Play 内置 Gemini Live AI 助手 + Game Trials 试玩功能
  </div>
  <div class="item-body">
    <strong>GDC 2026</strong> 宣布：Google Play Games 将内置 Gemini Live AI 助手，提供对话式游戏辅助。同时推出 <strong>Game Trials</strong> 功能，用户可免费试玩付费游戏，购买后保留进度。<strong>Buy Once Play Anywhere</strong> 实现一次购买移动端+PC 端同步。
  </div>
  <div class="stat-row">
    <span class="stat">🎮 <em>Gemini AI</em></span>
    <span class="stat">🆓 <em>免费试玩</em></span>
    <span class="stat">🔄 <em>跨端同步</em></span>
  </div>
  <div class="item-source">来源：<a href="https://techcrunch.com/2026/03/11/google-play-is-adding-new-paid-and-pc-games-game-trials-community-posts-and-more/" target="_blank">TechCrunch</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">Google 正在将 AI 深度嵌入游戏生态。<strong>Gemini Live 不仅是语音助手，更是游戏攻略+陪伴式 AI</strong>。Game Trials 解决了付费游戏的最大痛点——"买完后悔"，这将显著提升转化率。跨端购买则模糊了移动和 PC 的边界，对 Steam 可能形成冲击。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    4月国产新机爆发：小米 16、Find X9 Ultra、Pura90 系列、阔折叠
  </div>
  <div class="item-body">
    微博 @数码闲聊站 爆料：4月暂定待发新机包括 <strong>小米 16</strong>、<strong>OPPO Find X9 Ultra</strong>、Find X9s Pro、<strong>华为 Pura90 系列</strong>、华为 Pura X2 阔折叠、天玑 9500 风扇性能机、天玑 9500 性能机。有性能机、有影像旗舰、有阔折叠。
  </div>
  <div class="stat-row">
    <span class="stat">📱 <em>小米 16</em></span>
    <span class="stat">📱 <em>Find X9 Ultra</em></span>
    <span class="stat">🏰 <em>Pura90</em></span>
    <span class="stat">📍 <em>4月发布</em></span>
  </div>
  <div class="item-source">来源：<a href="https://weibo.com/数码闲聊站" target="_blank">微博 @数码闲聊站</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">4月国产新机<strong>密集发布是供应链回暖的信号</strong>。小米 16 主打小直屏+大电池，Find X9 Ultra 主打影像（双 2 亿主摄），Pura90 是华为 P 系列的继任者，阔折叠是新品类。手机厂商从"降价保份额"转向"高端差异化"，旗舰机竞争进入新一轮配置竞赛。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-purple">💜制程</span>
    2nm 迭代旗舰：OPPO Find X9 Ultra 6.9 英寸 2D 纯直屏
  </div>
  <div class="item-body">
    微博 @数码闲聊站 独家爆料：<strong>2nm 迭代新旗舰大屏是 Find X9 Ultra</strong>，采用 <strong>6.9 英寸</strong> 2D 纯直屏形态，LIPO 极窄物理四等边，国产定制新基材，等效超清显示，1nit 低亮度显示，支持 BT.2020。
  </div>
  <div class="stat-row">
    <span class="stat">📏 <em>6.9英寸</em></span>
    <span class="stat">🖥️ <em>2D直屏</em></span>
    <span class="stat">🔬 <em>2nm制程</em></span>
    <span class="stat">📱 <em>Find X9 Ultra</em></span>
  </div>
  <div class="item-source">来源：<a href="https://weibo.com/数码闲聊站" target="_blank">微博 @数码闲聊站</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>Find X9 Ultra 6.9 英寸直屏是一个大胆的产品定位</strong>——大屏+直屏的组合在旗舰机中罕见（主流是曲屏），这可能是在对标 iPhone Pro Max 的手感，同时用直屏吸引"直屏党"。2nm 制程 + LIPO 边框意味着屏幕成本将创下新高。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-purple">💜制程</span>
    小米 16GB LPDDR6 + 1TB UFS 5.0 旗舰：成本首超 SoC
  </div>
  <div class="item-body">
    微博 @数码闲聊站 独家：<strong>小米</strong> 16GB LPDDR6 + 1TB UFS 5.0 新方案已开模，<strong>SM8975</strong>（骁龙 8 Elite Gen6 Pro）机型测试中，目前仅规划顶配版。<br><br>
    这套内存成本已远远超过 SM8975 SoC 成本——这是手机行业首次出现存储成本超过处理器成本的情况。该方案将用于对标 iPhone 18 Pro，整机价格或突破万元。
  </div>
  <div class="stat-row">
    <span class="stat">💾 <em>LPDDR6</em></span>
    <span class="stat">💿 <em>UFS 5.0</em></span>
    <span class="stat">📦 <em>16GB+1TB</em></span>
    <span class="stat">📱 <em>小米</em></span>
  </div>
  <div class="item-source">来源：<a href="https://new.qq.com/rain/a/20260312A04K8500" target="_blank">腾讯网</a>、<a href="https://weibo.com/数码闲聊站" target="_blank">微博 @数码闲聊站</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">内存成本超过 SoC 成本——<strong>这在手机行业是首次</strong>。过去都是"旗舰芯片=最高成本"，现在是存储成为瓶颈。LPDDR6 + UFS 5.0 将显著提升 AI 手机的本地模型能力，16GB RAM 意味着可以在手机上运行 10B 参数的本地模型。万元定价标志超高端市场门槛进一步提高。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    小米 16 小直屏旗舰：6.36 英寸 + 8000mAh + 潜望镜
  </div>
  <div class="item-body">
    微博 @数码闲聊站 独家：<strong>小米 16</strong> 小直屏迭代旗舰中杯，新开电池在争取 <strong>8000mAh±</strong>。确定有<strong>潜望镜</strong>、无线充、超声波指纹。<br><br>
    小米 16 将采用 6.36 英寸华星光电 M10 双层 OLED 直屏，Pro 版配备 6.8 英寸大屏。
  </div>
  <div class="stat-row">
    <span class="stat">📱 <em>6.36英寸</em></span>
    <span class="stat">🔋 <em>8000mAh</em></span>
    <span class="stat">📸 <em>潜望镜</em></span>
    <span class="stat">📱 <em>小米 16</em></span>
  </div>
  <div class="item-source">来源：<a href="https://www.163.com/dy/article/JPSSB8T505568VTV.html" target="_blank">网易</a>、<a href="https://weibo.com/数码闲聊站" target="_blank">微博 @数码闲聊站</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>小米 16 小直屏 + 8000mAh 是产品定义的精妙平衡</strong>——小屏手机最大痛点是续航，8000mAh 意味着可以重度用一天。潜望镜+无线充+超声波指纹的全配方案，说明小屏旗舰正在"去妥协化"。这是小米在高端市场的重要突破。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-new">🆕新品</span>
    14 英寸 AI 超轻薄笔记本：Intel PTL Ultra + 1KG
  </div>
  <div class="item-body">
    微博 @数码闲聊站 独家：14 英寸屏幕，Intel <strong>PTL Ultra5 325 / Ultra X7 358H</strong> 处理器，内存 24GB+1TB / 32GB+1T，重量 <strong>1KG±</strong>，定位 AI 超轻薄旗舰笔记本。
  </div>
  <div class="stat-row">
    <span class="stat">💻 <em>1KG</em></span>
    <span class="stat">🧠 <em>AI 本</em></span>
    <span class="stat">🔢 <em>32GB RAM</em></span>
  </div>
  <div class="item-source">来源：<a href="https://weibo.com/数码闲聊站" target="_blank">微博 @数码闲聊站</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>1KG 超轻薄 + 32GB RAM = AI PC 的理想形态</strong>。Intel PTL (Panther Lake) 是下一代移动处理器，AI PC 需要本地运行模型，32GB RAM 是底线。14 英寸 1KG 意味着可以随身携带随时办公。</div>
  </div>
</div>
"""
template = template.replace('{{SECTION_PHONE_ITEMS}}', phone_items)

# ==================== 3. 芯片与算力 ====================
chip_items = """
<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    NVIDIA 发布 Vera Rubin 平台：3nm + 3360 亿晶体管 + 2026 下半年出货
  </div>
  <div class="item-body">
    GTC 2026 正式发布 <strong>Vera Rubin</strong> AI 加速平台，采用台积电 3nm 工艺，集成 <strong>3360 亿颗晶体管</strong>（较 Blackwell 的 2080 亿提升超过 60%）。命名来自已故美国天文学家薇拉·鲁宾（暗物质发现者）。<br><br>
    Rubin GPU 在 NVFP4 精度下达 50 PFLOPS 推理算力、35 PFLOPS 训练算力，分别是 Blackwell 的 <strong>5 倍和 3.5 倍</strong>。
  </div>
  <div class="stat-row">
    <span class="stat">🔧 <em>3nm</em></span>
    <span class="stat">💿 <em>3360亿晶体管</em></span>
    <span class="stat">⚡ <em>5x 推理</em></span>
    <span class="stat">📅 <em>2026下半年</em></span>
  </div>
  <div class="item-source">来源：<a href="https://finance.sina.com.cn/tech/digi/2026-03-16/doc-inhrctqs8940923.shtml" target="_blank">新浪财经</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">Vera Rubin 是 NVIDIA 的<strong>年度重磅更新</strong>。从 Blackwell 到 Rubin 仅一年迭代，说明 AI 算力需求已经"等不及"了。5 倍推理性能提升意味着：同等算力下，成本可以降低 80%。2027 年 1 万亿美元订单目标是"甜蜜的负担"——NVIDIA 必须产能翻倍才能满足。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    NVIDIA 万亿订单：2027 年 Blackwell + Rubin 收入目标 1 万亿美元
  </div>
  <div class="item-body">
    黄仁勋在 GTC 2026 主题演讲中宣布，预计到 <strong>2027 年</strong>，Blackwell 与 Vera Rubin 两代芯片所产生的采购订单总额将达到 <strong>1万亿美元</strong>。这一数字是去年英伟达自己预测的整整两倍（去年预期 5000 亿）。<br><br>
    英伟达已连续 11 个季度实现超过 55% 的营收增长，本季度营收预计同比增长约 77%，达到约 780 亿美元。
  </div>
  <div class="stat-row">
    <span class="stat">💰 <em>1万亿美元</em></span>
    <span class="stat">📈 <em>77% 增长</em></span>
    <span class="stat">🔢 <em>翻倍</em></span>
  </div>
  <div class="item-source">来源：<a href="https://finance.sina.com.cn/tech/digi/2026-03-16/doc-inhrctqs8940923.shtml" target="_blank">新浪财经</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>1 万亿美元 = 苹果市值</strong>——NVIDIA 凭芯片就能达到全球第一公司的体量。这是 AI 时代的"卖铲人"逻辑：不管谁赢得 AI 竞赛，都需要 NVIDIA 的算力。但 5000 亿→1 万亿的"翻倍预期"也意味着供应链压力巨大，任何产能问题都会被放大。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-purple">💜制程</span>
    NVIDIA Feynman 架构：1.6nm + 硅光子 + 2028 年量产
  </div>
  <div class="item-body">
    黄仁勋公布 <strong>Feynman</strong> 架构：全球首款面向世界模型与物理 AI 的下一代 GPU，提前两年曝光原型。采用台积电 <strong>1.6nm A16</strong> 工艺，搭载硅光子光互连，带宽提升 <strong>10 倍</strong>、能耗降低 <strong>90%</strong>，推理性能为 Blackwell 的 5 倍，计划 <strong>2028 年</strong> 量产。
  </div>
  <div class="stat-row">
    <span class="stat">🔧 <em>1.6nm</em></span>
    <span class="stat">💡 <em>硅光子</em></span>
    <span class="stat">📅 <em>2028</em></span>
    <span class="stat">⚡ <em>5x 推理</em></span>
  </div>
  <div class="item-source">来源：<a href="https://finance.sina.com.cn/tech/digi/2026-03-16/doc-inhrctqs8940923.shtml" target="_blank">新浪财经</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>Feynman = 物理 AI 的基础设施</strong>。世界模型需要理解物理世界（重力、碰撞、因果），这需要前所未有的算力。1.6nm + 硅光子的组合是"终极方案"——带宽瓶颈被光互连彻底打破。2028 年量产意味着还有两年"等待期"。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-blue">🔧技术</span>
    NVIDIA Groq 3 LPU：收购后首款芯片 + Q3 出货
  </div>
  <div class="item-body">
    英伟达发布 <strong>Groq 3 LPU</strong>（Language Processing Unit），这是自去年 12 月以 200 亿美元收购 Groq 以来推出的首款芯片。预计 <strong>第三季度</strong> 开始出货。<br><br>
    推理过程分为两步：Vera Rubin 芯片负责"预填充"（将用户请求从人类语言转换为 token），Groq 芯片负责"解码"（生成答案）。LPX 推理机柜将于 2026-2027 年推出。
  </div>
  <div class="stat-row">
    <span class="stat">🧠 <em>LPU</em></span>
    <span class="stat">📅 <em>Q3 出货</em></span>
    <span class="stat">💰 <em>200亿收购</em></span>
  </div>
  <div class="item-source">来源：<a href="https://finance.sina.com.cn/tech/digi/2026-03-16/doc-inhrctqs8940923.shtml" target="_blank">新浪财经</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">Groq 的"异构推理"思路正在成为行业标准：<strong>预填充和解码分离</strong>，用不同芯片优化不同阶段。200 亿美元收购后快速推出产品，说明 NVIDIA 对"推理市场"志在必得。LPX 推理机柜是面向数据中心的完整方案。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-blue">🔧技术</span>
    NVIDIA DLSS 5：AI 驱动游戏图形突破 + 今年秋季推出
  </div>
  <div class="item-body">
    NVIDIA 宣布 <strong>DLSS 5</strong> 将于今年秋季推出，这是 AI 驱动的游戏图形技术突破，注入逼真光照和材质，为游戏带来前所未有的视觉体验。
  </div>
  <div class="stat-row">
    <span class="stat">🎮 <em>DLSS 5</em></span>
    <span class="stat">🍂 <em>秋季发布</em></span>
    <span class="stat">✨ <em>光追突破</em></span>
  </div>
  <div class="item-source">来源：<a href="https://twitter.com/NVIDIA" target="_blank">@NVIDIA (Twitter)</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">DLSS 5 是 NVIDIA 的<strong>游戏护城河</strong>——AMD FSR 和 Intel XeSS 难以匹敌。AI 超分辨率技术让中端显卡也能跑 4K 光追，这是 NVIDIA 维持市场份额的关键。游戏玩家买 NVIDIA，本质上是在买"AI 驱动"的画质提升。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-orange">💰投资</span>
    Jensen：推理拐点已至，AI 算力需求两年激增百万倍
  </div>
  <div class="item-body">
    黄仁勋在 GTC 2026 表示："<strong>推理的拐点已经到来</strong>，需求还在不断增长。"过去两年 AI 的计算需求激增了 <strong>百万倍</strong>，说明推理任务对算力的消耗远超训练阶段。AI 使用量持续攀升，推理能力已成为当前 AI 发展的核心瓶颈。
  </div>
  <div class="stat-row">
    <span class="stat">📊 <em>百万倍</em></span>
    <span class="stat">🎯 <em>推理拐点</em></span>
    <span class="stat">⚠️ <em>算力瓶颈</em></span>
  </div>
  <div class="item-source">来源：<a href="https://finance.sina.com.cn/tech/digi/2026-03-16/doc-inhrctqs8940923.shtml" target="_blank">新浪财经</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>"百万倍"是一个惊人的数字</strong>——从 2024 到 2026，AI 推理需求增长了 100 万倍。这解释了为什么 NVIDIA 的订单永远做不完：每个 AI 应用都在"吞噬"算力。未来的算力缺口可能比想象中更大。</div>
  </div>
</div>
"""
template = template.replace('{{SECTION_CHIP_ITEMS}}', chip_items)

# ==================== 4. 游戏行业 ====================
game_items = """
<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    Google Play Game Trials：试玩付费游戏 + 购买后保留进度
  </div>
  <div class="item-body">
    GDC 2026 宣布 Google Play 推出 <strong>Game Trials</strong> 功能，用户可以免费试玩付费游戏，体验后决定是否购买，且<strong>购买后保留试玩进度</strong>。
  </div>
  <div class="stat-row">
    <span class="stat">🆓 <em>免费试玩</em></span>
    <span class="stat">💾 <em>保留进度</em></span>
    <span class="stat">📈 <em>提升转化</em></span>
  </div>
  <div class="item-source">来源：<a href="https://techcrunch.com/2026/03/11/google-play-is-adding-new-paid-and-pc-games-game-trials-community-posts-and-more/" target="_blank">TechCrunch</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content">Game Trials 解决了付费游戏的最大转化痛点。<strong>"先试后买"在手游时代迟到太久</strong>——玩家不用担心"花钱买后悔"，开发商不用担心"被白嫖"。保留进度是关键：试玩时的游戏进度和道具可以继承到正式版。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-new">🆕新品</span>
    Google Play Buy Once Play Anywhere：一次购买移动端 + PC 端
  </div>
  <div class="item-body">
    Google Play 推出 <strong>Buy Once Play Anywhere</strong> 政策，实现一次购买即可在移动端和 PC 端同步游玩。同时推出独立的 PC 游戏商店区。
  </div>
  <div class="stat-row">
    <span class="stat">💻 <em>PC 端</em></span>
    <span class="stat">📱 <em>移动端</em></span>
    <span class="stat">🔄 <em>一次购买</em></span>
  </div>
  <div class="item-source">来源：<a href="https://techcrunch.com/2026/03/11/google-play-is-adding-new-paid-and-pc-games-game-trials-community-posts-and-more/" target="_blank">TechCrunch</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>Google 正在模糊移动和 PC 游戏的边界</strong>。这直接对标 Steam 和 Epic。独立 PC 游戏商店意味着 Google 不再满足于"Android 游戏平台"，而是要成为"全平台游戏发行商"。</div>
  </div>
</div>
"""
template = template.replace('{{SECTION_GAME_ITEMS}}', game_items)

# ==================== 5. 科技行业动态 ====================
industry_items = """
<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    阿里成立 ATH 事业群：CEO 吴泳铭挂帅，聚焦 AI Agent
  </div>
  <div class="item-body">
    <strong>3 月 16 日，阿里巴巴正式成立新事业群 AlibabaTokenHub（ATH）</strong>，由集团 CEO <strong>吴泳铭</strong> 直接负责，与电商事业群、阿里云智能事业群并列，成为阿里最核心的事业群之一。<br><br>
    ATH 以"创造 Token、输送 Token、应用 Token"为核心目标，涵盖五大事业部：通义实验室、MaaS 业务线、千问事业部、<strong>悟空事业部</strong>（首次曝光，专注 B 端 AI 原生工作平台）、AI 创新事业部。
  </div>
  <div class="stat-row">
    <span class="stat">🏢 <em>ATH 事业群</em></span>
    <span class="stat">👤 <em>吴泳铭挂帅</em></span>
    <span class="stat">🔧 <em>5 大事业部</em></span>
    <span class="stat">🎯 <em>AI Agent</em></span>
  </div>
  <div class="item-source">来源：<a href="https://new.qq.com/rain/a/20260316A08JY300" target="_blank">腾讯网</a>、<a href="https://www.sohu.com/a/997286165_121885030" target="_blank">搜狐</a>、<a href="https://www.163.com/dy/content/KO5U3277051196HN.html" target="_blank">网易新闻</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>阿里 ATH 事业群的成立是" Token 经济学"在组织架构上的落地</strong>。从"模型"到"Token"的战略升级，意味着阿里不再只是卖模型，而是要构建完整的 AI Agent 生态。悟空事业部的 B 端定位剑指企业市场——这是阿里在 AI 领域对抗字节的关键布局。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    元宝 App 更新：可共同养虾 + 一键创建即将上线
  </div>
  <div class="item-body">
    腾讯 <strong>元宝 App</strong> 更新至 v2.60.10 及以上版本，用户可将 OpenClaw 接入元宝派<strong>共同养虾</strong>。支持三种接入方式：命令接入、通道配置、扫码关联。<br><br>
    近期将上线限量免费<strong>"一键创建 OpenClaw"</strong>活动，用户无需复杂配置即可在元宝派内直接创建并启用自己的 Bot，与派友一起"养虾"。
  </div>
  <div class="stat-row">
    <span class="stat">🦐 <em>共同养虾</em></span>
    <span class="stat">🆓 <em>一键创建</em></span>
    <span class="stat">📱 <em>v2.60.10</em></span>
  </div>
  <div class="item-source">来源：<a href="https://new.qq.com/rain/a/20260317A04JY200" target="_blank">腾讯网</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>元宝 + OpenClaw 是腾讯的"Agent 生态"布局</strong>。"养虾"本质上是一种轻量级的 Agent 使用场景——用户不需要懂技术，就能体验 AI 自动化。"一键创建"降低门槛，"共同养虾"增加社交粘性。这是腾讯对抗豆包、Kimi 的差异化策略。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-hot">🔥热点</span>
    SuperAI 2026 大会：6 月新加坡举办 + 10000+ 领袖参加
  </div>
  <div class="item-body">
    <strong>SuperAI 2026</strong> 大会将于 6 月在新加坡举办，预计有 <strong>10000+</strong> 科技行业领袖参加。SuperAI 是关注人工智能发展的顶级会议。
  </div>
  <div class="stat-row">
    <span class="stat">🇸🇬 <em>新加坡</em></span>
    <span class="stat">👥 <em>10000+</em></span>
    <span class="stat">📅 <em>6月</em></span>
  </div>
  <div class="item-source">来源：<a href="https://twitter.com/superai_conf" target="_blank">@superai_conf (Twitter)</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>SuperAI 选址新加坡是"安全考量"</strong>——中美科技竞争的背景下，新加坡是少数两边都"说得上话"的地方。10000+ 参会规模说明 AI 热度不减，会议可能成为亚洲版的"AI春晚"。</div>
  </div>
</div>

<div class="item">
  <div class="item-title">
    <span class="tag tag-blue">🔧技术</span>
    小度接入 OpenClaw 龙虾生态：语音控制电脑
  </div>
  <div class="item-body">
    小度上周宣布接入 <strong>OpenClaw 龙虾生态</strong>，小度智能家居 Skills 已登陆 ClawHub。用户在家说话即可控制电脑，实现智能家居与 AI 代理的深度融合。
  </div>
  <div class="stat-row">
    <span class="stat">🏠 <em>智能家居</em></span>
    <span class="stat">🗣️ <em>语音控制</em></span>
    <span class="stat">💻 <em>控制电脑</em></span>
  </div>
  <div class="item-source">来源：<a href="https://weibo.com/ithome" target="_blank">微博 @IT之家</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>语音 + Agent = 下一代人机交互</strong>。小度是中国最大的智能家居平台之一，接入 OpenClaw 意味着你可以"用嘴指挥 AI 干活"。这比"对着屏幕打字"自然得多，是 AI Agent 大众化的重要路径。</div>
  </div>
</div>
"""
template = template.replace('{{SECTION_INDUSTRY_ITEMS}}', industry_items)

# ==================== 6. 政策与监管 ====================
policy_items = """
<div class="item">
  <div class="item-title">
    <span class="tag tag-orange">💰投资</span>
    微软声援 Anthropic：首家在供应链风险争端中站队
  </div>
  <div class="item-body">
    美国五角大楼将 Anthropic 列为"供应链风险"后，微软公开声援 Anthropic，成为首家在 Anthropic 与美国国防部争端中站队的科技巨头。英伟达则承载全球三分之一的 AI 算力，Anthropic、Meta 等公司均选择与英伟达合作。
  </div>
  <div class="stat-row">
    <span class="stat">🏛️ <em>供应链</em></span>
    <span class="stat">🇺🇸 <em>美国国防部</em></span>
    <span class="stat">🤝 <em>微软声援</em></span>
  </div>
  <div class="item-source">来源：<a href="https://www.163.com/dy/content/KO5U3277051196HN.html" target="_blank">网易新闻</a></div>
  <div class="insight-box">
    <div class="insight-label">💡 深度洞察</div>
    <div class="insight-content"><strong>微软 vs 国防部：AI 安全的"企业 vs 政府"博弈</strong>。微软为 Anthropic 站台，本质上是在为"开放 AI 开发"辩护。如果国防部赢了，所有 AI 公司都可能面临供应链审查。这场较量的结果将定义未来 10 年 AI 行业的监管走向。</div>
  </div>
</div>
"""
template = template.replace('{{SECTION_POLICY_ITEMS}}', policy_items)

template = template.replace('{{SECTION_GITHUB_ITEMS}}', '')

output_file = f"brief/{today.strftime('%Y-%m-%d')}.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(template)

print(f"✅ 已生成日报: {output_file}")
