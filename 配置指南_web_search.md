# 配置 Brave Search API 指南

## 步骤 1：获取 API Key

1. 访问：https://brave.com/search/api/
2. 点击 "Get Started" 或 "Sign Up"
3. 注册账号（可以用 Google/GitHub/Microsoft 账号）
4. 进入 Dashboard
5. 创建新的 API Key
6. 复制 API Key（格式类似：BSA******************）

**免费额度**：
- 每月 2000 次免费查询
- 足够个人使用

## 步骤 2：配置到 OpenClaw

### 方法 A：环境变量（推荐）
```bash
# 临时设置（当前会话）
export BRAVE_API_KEY="你的API_KEY"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export BRAVE_API_KEY="你的API_KEY"' >> ~/.bashrc
source ~/.bashrc
```

### 方法 B：配置文件
```bash
# 编辑配置文件
nano ~/.openclaw/openclaw.json

# 在文件中添加（如果不存在 web 配置）：
{
  "web": {
    "search": {
      "provider": "brave",
      "apiKey": "你的API_KEY"
    }
  }
}
```

## 步骤 3：测试
```bash
# 重启 OpenClaw
openclaw gateway restart

# 测试搜索（在对话中让我执行）
# 我会运行：web_search(query="测试查询")
```

## 获取链接
- API 文档：https://brave.com/search/api/documentation/
- Dashboard：https://api.search.brave.com/app/dashboard
- 定价：https://brave.com/search/api/pricing/
