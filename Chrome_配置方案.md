# AgentWebSearch Chrome 配置方案

## 当前问题
AgentWebSearch 需要启动 Chrome 浏览器，但脚本默认使用 `google-chrome` 命令。

## 方案 1：使用 Windows Chrome（推荐）

### 优势：
- ✅ Windows 上已经安装了 Chrome
- ✅ 不需要在 WSL2 内安装
- ✅ 可以使用现有的登录状态

### 步骤：
1. 创建一个包装脚本
```bash
cd ~/AgentWebSearch-MCP
nano chrome-wrapper.sh
```

2. 添加内容：
```bash
#!/bin/bash
# 使用 Windows Chrome
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" "$@"
```

3. 给脚本执行权限：
```bash
chmod +x chrome-wrapper.sh
```

4. 修改 chrome_launcher.py：
```bash
nano chrome_launcher.py
# 找到 "google-chrome" 改为 "./chrome-wrapper.sh"
```

## 方案 2：在 WSL2 内安装 Chrome

### 步骤：
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

### 缺点：
- ❌ 需要下载安装（~100MB）
- ❌ 需要 X server 才能显示 GUI（但这个工具使用 CDP，不需要显示）
- ❌ 占用更多空间

## 方案 3：使用 Chromium（轻量级）

### 步骤：
```bash
sudo apt-get install -y chromium-browser
```

### 修改 chrome_launcher.py：
```bash
# 找到 "google-chrome" 改为 "chromium-browser"
```

## 我的建议

**方案 1（使用 Windows Chrome）** - 最简单，不需要安装任何东西。

**你想选哪个方案？** 或者我直接帮你配置方案 1？
