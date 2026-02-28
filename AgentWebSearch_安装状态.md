# AgentWebSearch-MCP 安装状态

## ✅ 已完成
1. ✅ 项目已下载到 ~/AgentWebSearch-MCP
2. ✅ Python 3.10.12 已安装

## ❌ 遇到问题
需要安装 pip3 和 venv，但需要 sudo 权限

## 解决方案

### 方法 1：手动安装 pip（推荐）
```bash
# 在终端执行（需要输入密码）
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# 然后继续
cd ~/AgentWebSearch-MCP
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 方法 2：用 conda（如果已安装）
```bash
cd ~/AgentWebSearch-MCP
conda create -p ./venv python=3.10
conda activate ./venv
pip install -r requirements.txt
```

### 方法 3：用系统 Python（不推荐）
```bash
cd ~/AgentWebSearch-MCP
pip3 install --user -r requirements.txt
```

## requirements.txt 内容
```
mcp>=1.0.0
playwright>=1.40.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

## 下一步（pip 安装完成后）

1. 创建虚拟环境
```bash
cd ~/AgentWebSearch-MCP
python3 -m venv venv
source venv/bin/activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 安装 Playwright 浏览器
```bash
playwright install chromium
```

4. 启动 Chrome 实例
```bash
python chrome_launcher.py start
```

5. 配置到 OpenClaw
```bash
openclaw mcp add agentwebsearch -- python ~/AgentWebSearch-MCP/mcp_server.py
```

6. 重启 OpenClaw
```bash
openclaw gateway restart
```

## 测试
安装完成后，告诉我，我会测试搜索功能！

---
**当前状态**：等待 sudo 权限安装 pip3
