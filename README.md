# 科技资讯日报

> **⚠️ AI 执行入口：生成日报前必须读完本文件。**

本文件夹是科技资讯日报系统的完整工作目录，包含从采集、选题、撰写到发布的全流程。

---

## 目录结构

```
科技资讯日报-new/
├── README.md                    ← 本文件（AI 执行入口）
├── template.html                ← 日报 HTML 模板（必须基于此模板生成）
├── brief/                       ← 日报 HTML 输出目录
│   └── YYYY-MM-DD.html
├── collect/                     ← RSS + X 采集系统
│   ├── collect.py               ← 采集主脚本（python3 collect/collect.py）
│   ├── requirements.txt
│   └── sources/
│       ├── sources.yaml         ← 信源配置（官方RSS + 媒体RSS + X账号）
│       └── filters.yaml         ← 关键词过滤规则
├── selection/                   ← 选题报告（AI 输出的 Markdown）
│   └── selection_YYYYMMDD.md
├── scripts/                     ← 发布脚本（邮件 / 公众号 / GitHub）
│   ├── send_email.py
│   └── publish_all.py
└── workflow/                    ← 工作流配置文件
    ├── 02-selection/
    │   └── news-preferences.md  ← 选题偏好（选哪些新闻）
    ├── 03-generation/
    │   └── writing-preferences.md ← 撰写偏好（怎么写）
    └── 04-publishing/
        └── steps.md             ← 发布步骤
```

---

## 完整日报流程

### Step 1：采集

```bash
cd "/Users/yangliu/Documents/Claude Code/科技资讯日报-new"
python3 collect/collect.py
# 输出到 collect/output/YYYY-MM-DD.md
```

可选参数：`--skip-x`（跳过X采集）、`--hours 72`（扩大时间窗口）

### Step 2：选题

```bash
bash scripts/step2-selection.sh
```

脚本会把选题规则完整输出到屏幕，AI 据此生成选题报告 → `selection/selection_YYYYMMDD.md`。
**人工确认选题后，再进入 Step 3。**

### Step 3：撰写日报

```bash
bash scripts/step3-writing.sh
```

脚本会把撰写规范完整输出到屏幕，AI 据此撰写日报 → `brief/YYYY-MM-DD.html`。

### Step 4：发布同步（GitHub + 测试邮件 + 公众号）

```bash
bash scripts/step4-publish.sh brief/YYYY-MM-DD.html
```

三步同时完成。确认测试邮件 OK 后，执行群发：

```bash
bash scripts/step4-sendall.sh brief/YYYY-MM-DD.html
# 会显示收件人列表，需手动输入 yes 才能发送
```

---

## 信源说明

信源分三层，配置在 `collect/sources/sources.yaml`：

| 层级 | 说明 | 数量规则 |
|------|------|----------|
| 官方信源 | 官方博客 RSS（OpenAI/NVIDIA/Google 等） | 48h 内有几条取几条 |
| 英文媒体 | TechCrunch/The Verge/Wired 等 | 每源取48h内所有，上限30条 |
| X 账号 | P1 必采 / P2 选采 | P1：@sama/@karpathy 等核心人物 |

增删信源：直接编辑 `collect/sources/sources.yaml`。
