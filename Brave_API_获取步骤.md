# Brave Search API 免费获取步骤

## 当前页面：订阅页面
你现在在：https://api-dashboard.search.brave.com/app/subscriptions/subscribe

## 步骤指南

### 1️⃣ 选择免费套餐
在订阅页面应该会看到几个选项：
- **Free Tier（免费套餐）** - 每月 2000 次查询
- Pro Tier - 付费套餐

**操作**：
- 选择 "Free" 或 "Free Tier"
- 点击 "Subscribe" 或 "Get Started"

### 2️⃣ 确认订阅
可能需要：
- 确认账号信息
- 同意服务条款
- 点击 "Confirm" 或 "Subscribe"

### 3️⃣ 获取 API Key
订阅完成后：
1. 会自动跳转到 Dashboard
   - 或者手动访问：https://api-dashboard.search.brave.com/app/dashboard

2. 在 Dashboard 找到：
   - "API Keys" 选项
   - 或者 "Generate New Key" 按钮

3. 点击生成新的 API Key
   - 给 key 起个名字（比如 "OpenClaw"）
   - 点击 "Generate" 或 "Create"

4. **复制 API Key**
   - 格式类似：`BSA...` 开头的长字符串
   - **重要**：只显示一次，务必保存！

## 免费额度说明
- **每月 2000 次查询**
- 足够个人使用
- 每月 1 号重置
- 超出后需要付费或等下月

## 获取到 API Key 后

### 方法 1：告诉我（推荐）
通过**飞书私聊**把 API Key 发给我：
- 不要在公开渠道发送
- 我会帮你配置到 OpenClaw

### 方法 2：自己配置
```bash
# 临时设置（重启后失效）
export BRAVE_API_KEY="你的API_KEY"

# 永久设置（推荐）
echo 'export BRAVE_API_KEY="你的API_KEY"' >> ~/.bashrc
source ~/.bashrc

# 重启 OpenClaw
openclaw gateway restart
```

### 方法 3：配置文件
编辑 `~/.openclaw/openclaw.json`，添加：
```json
{
  "web": {
    "search": {
      "provider": "brave",
      "apiKey": "你的API_KEY"
    }
  }
}
```

## 验证配置
配置完成后，让我执行测试：
```
web_search(query="测试查询")
```

## 如果页面没有 Free 选项
可能的原因：
1. 已经订阅过了 → 直接去 Dashboard 获取 key
2. 需要先验证邮箱 → 检查邮箱
3. 区域限制 → 尝试换个网络

## 常见问题

**Q: 找不到 "Generate Key" 按钮？**
A: 可能需要先创建一个项目或应用，然后再生成 key

**Q: API Key 在哪里看？**
A: Dashboard → API Keys → 点击已有的 key 可以查看（部分显示）

**Q: 免费套餐够用吗？**
A: 2000 次/月，相当于每天 66 次搜索，完全够个人使用

---

## 下一步
1. 按照上述步骤获取 API Key
2. 通过飞书私聊发给我
3. 我帮你配置并测试

拿到 key 后告诉我！🦞
