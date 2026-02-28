# AgentWebSearch 无密码安装方案

## 问题
- 需要 sudo 安装 python3-pip 和 python3-venv
- 但你不知道/不想提供密码

## 方案 1：在你的终端执行（推荐）

### 步骤：
1. 打开 Ubuntu 终端（不是在这里）
2. 输入命令，会提示输入密码：
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv
   # 输入你的登录密码（屏幕不会显示）
   ```
3. 完成后告诉我，我继续安装

## 方案 2：用 Windows Python（临时）

### 在 Windows 上：
1. 安装 Python（如果还没有）：https://www.python.org/downloads/
2. 在 PowerShell 中：
   ```powershell
   cd \\wsl.localhost\Ubuntu-22.04\home\huang777\AgentWebSearch-MCP
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 方案 3：暂时用 Brave API（最快）

### 优势：
- ✅ 不需要安装任何东西
- ✅ 你已经在 Brave 网站上了
- ✅ 只需要获取 API Key
- ✅ 我能立即开始搜索

### 步骤：
1. 在 Brave 网站获取 API Key
2. 通过飞书私聊发给我
3. 我配置后立即能搜索

## 方案 4：重置 WSL2 密码

如果你真的忘记了密码：

### 在 Windows PowerShell（管理员）：
```powershell
wsl -u root
passwd huang777
# 输入新密码两次
exit
```

然后在 Ubuntu 中用新密码。

## 我的建议

**最快方案**：方案 3（Brave API）
- 5 分钟内就能开始搜索
- 不需要安装任何东西
- 免费 2000 次/月够用

**最彻底方案**：方案 1（在终端输入密码）
- 一次配置，长期使用
- AgentWebSearch 更强大（支持中文、可登录）

---

**你想选哪个方案？告诉我！** 🦞
