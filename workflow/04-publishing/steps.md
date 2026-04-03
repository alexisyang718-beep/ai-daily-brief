# 发布流程步骤

## 前置条件

- 日报文件已生成：`brief/YYYY-MM-DD.html`
- 已确认内容无误

---

## 正确发布顺序

```
Step 4a：GitHub 同步 + 测试邮件 + 公众号草稿  ←── 三步同时完成，用 publish_all.py
           ↓
        等待用户确认测试邮件 OK
           ↓
Step 4b：群发（23人）  ←── 用户确认后才能执行
```

**⚠️ 禁止在用户确认测试邮件之前执行群发**

---

## Step 4a：三步同时发布

```bash
cd "/Users/yangliu/Documents/Claude Code/科技资讯日报-new"
python3 scripts/publish_all.py brief/YYYY-MM-DD.html
```

这一步同时完成：
1. **GitHub 同步**：push 到 GitHub Pages
2. **测试邮件**：发送给 alexisyang@tencent.com
3. **公众号草稿**：同步到微信公众号草稿箱

执行完成后，告知用户"已完成 GitHub 同步、测试邮件已发、公众号草稿已同步，请确认测试邮件后告诉我是否群发"。

---

## Step 4b：群发（用户确认后才执行）

确认用户说"OK群发"或类似指令后：

```bash
cd "/Users/yangliu/Documents/Claude Code/科技资讯日报-new"
bash scripts/step4-sendall.sh brief/YYYY-MM-DD.html
# 会显示收件人列表（23人），需手动输入 yes 确认后发送
```

---

## 发布后验证

- [ ] GitHub Pages 可访问（`https://alexisyang718-beep.github.io/ai-archive/brief/YYYY-MM-DD.html`）
- [ ] 测试邮件已收到并确认 OK
- [ ] 公众号草稿已生成
- [ ] 群发完成（23人）
