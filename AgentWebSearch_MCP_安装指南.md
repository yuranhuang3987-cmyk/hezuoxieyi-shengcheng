# AgentWebSearch-MCP - 最佳免费搜索方案

## 为什么这个最好？

| 功能 | Brave API | 我的笨办法 | AgentWebSearch-MCP |
|------|-----------|-----------|-------------------|
| API Key | 需要 | 不需要 | **不需要** ✅ |
| 成本 | 免费/付费 | 免费 | **完全免费** ✅ |
| 中文支持 | 一般 | 差 | **支持 Naver** ✅ |
| 机器人检测 | 无 | 容易被封 | **绕过** ✅ |
| CAPTCHA | 无 | 容易触发 | **抵抗** ✅ |
| OpenClaw 支持 | ❌ | ❌ | **✅ 原生支持** |

## 工作原理

```
你的电脑
├─ Chrome:9222 (Naver 搜索)
├─ Chrome:9223 (Google 搜索)
├─ Chrome:9224 (Brave 搜索)
└─ MCP Server
    └─ OpenClaw (我!)
```

**关键**：使用**真实 Chrome 浏览器**，不是无头浏览器！
- 就像你手动打开浏览器搜索一样
- 不会被识别为机器人
- 可以保存登录状态
- 完全免费

## 功能对比

| 工具 | 描述 | 需要 LLM |
|------|------|---------|
| web_search | 并行搜索 Naver/Google/Brave | ❌ |
| fetch_urls | 抓取网页内容 | ❌ |
| smart_search | 搜索 + 自动抓取（可控制深度） | ❌ |
| get_search_status | 检查搜索进度 | ❌ |
| cancel_search | 取消搜索并返回部分结果 | ❌ |
| agentcpm | AI 代理搜索（需要模型） | ✅ |

## 安装步骤

### 1. 下载项目
```bash
cd ~
git clone https://github.com/insung8150/AgentWebSearch-MCP.git
cd AgentWebSearch-MCP
```

### 2. 安装依赖
```bash
python3 -m venv venv
source venv/bin activate
pip install -r requirements.txt
```

### 3. 启动 Chrome 实例
```bash
python chrome_launcher.py start  # 启动 3 个 Chrome 实例
python chrome_launcher.py status  # 检查状态
```

### 4. 添加到 OpenClaw
```bash
# 方法 A：使用命令行
openclaw mcp add agentwebsearch -- python /home/huang777/AgentWebSearch-MCP/mcp_server.py

# 方法 B：编辑配置文件
nano ~/.openclaw/openclaw.json
```

在配置文件中添加：
```json
{
  "mcpServers": {
    "agentwebsearch": {
      "command": "python",
      "args": ["/home/huang777/AgentWebSearch-MCP/mcp_server.py"],
      "env": {}
    }
  }
}
```

### 5. 重启 OpenClaw
```bash
# 如果 gateway 在运行
pkill -f openclaw

# 重新启动
openclaw gateway
```

## 使用示例

安装后，我就能直接使用：

```
我：让我搜索一下 AI 知识付费的案例
→ 自动调用 web_search
→ 并行搜索 Naver/Google/Brave
→ 返回结果

我：深度搜索 Felix Craft 的商业模式
→ 调用 smart_search(depth="deep")
→ 搜索 + 抓取前 15 个网页
→ 返回详细分析
```

## 搜索深度选项

| 深度 | 描述 | 速度 | 内容 |
|------|------|------|------|
| simple | 只返回摘要 | 快（~35s） | 3K tokens |
| medium | 抓取前 5 个 URL | 中（~50s） | 17K tokens |
| deep | 抓取前 15 个 URL | 慢（~170s） | 77K tokens |

## 高级功能

### 1. 持久化登录
```bash
# 启动 Chrome 后，在打开的窗口中登录
# Google 账号 → 同步
# 这样 OAuth 登录和保存的密码都能用
```

### 2. 指定搜索引擎
```
portal="all"      # 并行搜索所有（默认）
portal="naver"    # 只搜索 Naver（中文友好）
portal="google"   # 只搜索 Google
portal="brave"    # 只搜索 Brave
```

### 3. 部分结果支持
如果搜索太慢：
- `get_search_status` - 查看进度和部分结果
- `cancel_search` - 取消搜索，返回已收集的结果

## 优势总结

✅ **完全免费** - 不需要任何 API key
✅ **不会被封** - 真实浏览器，不会被识别为机器人
✅ **支持中文** - Naver 搜索中文内容
✅ **OpenClaw 原生** - 专门为 OpenClaw 设计
✅ **持续更新** - 8 天前刚更新
✅ **并行搜索** - 同时搜索 3 个引擎
✅ **绕过 CAPTCHA** - 真实浏览器会话
✅ **可登录** - 保存登录状态，个性化搜索

## 常见问题

**Q: 需要一直开着 Chrome 吗？**
A: 是的，需要 3 个 Chrome 窗口。可以在后台运行。

**Q: 占用多少资源？**
A: 每个 Chrome 实例约 200-500MB 内存，总共约 1GB。

**Q: 能搜索小红书吗？**
A: 可以！登录后可以搜索任何网站。

**Q: 比 Brave API 好在哪？**
A:
- 完全免费（Brave 只有 2000 次/月）
- 支持中文（Brave 中文结果较少）
- 可以登录（个性化搜索）
- 不会被限制

## 下一步

1. 我帮你执行安装命令
2. 测试搜索功能
3. 开始研究竞品和市场

准备好了吗？我现在就开始安装！🦞
