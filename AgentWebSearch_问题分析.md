# AgentWebSearch 配置问题分析

## 当前状态
- ✅ Python 虚拟环境已创建
- ✅ 依赖已安装
- ✅ Chrome 进程已启动（3 个实例）
- ❌ CDP 端口无法连接（9222/9223/9224）

## 问题原因

**Windows Chrome 在 WSL2 中运行的端口绑定问题**

当在 WSL2 中启动 Windows Chrome 时：
- Chrome 进程在 Windows 上运行
- 端口绑定在 Windows 的 localhost
- WSL2 的 localhost 和 Windows 的 localhost 是不同的
- 导致 WSL2 内无法连接到 Windows Chrome 的 CDP 端口

## 解决方案

### 方案 1：使用 WSL2 内的 Chromium（推荐）

```bash
# 安装 Chromium
sudo apt-get install -y chromium-browser

# 修改 chrome_launcher.py
# 把 "./chrome-wrapper.sh" 改为 "chromium-browser"
```

**优势**：
- ✅ 端口绑定在 WSL2 内
- ✅ 可以直接访问
- ✅ 不需要复杂的网络配置

### 方案 2：使用 Windows IP 地址

1. 获取 Windows IP：
```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

2. 修改 chrome_launcher.py 连接到 Windows IP 的端口

**缺点**：
- ❌ 需要配置 Windows 防火墙
- ❌ 配置复杂
- ❌ 可能有安全问题

### 方案 3：暂时使用 Brave API（最快）

**优势**：
- ✅ 不需要配置
- ✅ 立即可用
- ✅ 你已经在 Brave 网站上了

## 我的建议

**方案 1（安装 Chromium）** - 最彻底，一劳永逸

**或者方案 3（用 Brave API）** - 最快，现在就能开始

你想选哪个？或者我帮你安装 Chromium？
