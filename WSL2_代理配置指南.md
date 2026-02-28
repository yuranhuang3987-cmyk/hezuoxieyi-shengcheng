# WSL2 使用 Windows 代理配置指南

## 步骤 1：获取 Windows 主机 IP

```bash
# 获取 Windows 主机 IP（WSL2 的网关）
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
echo "Windows IP: $WINDOWS_IP"
```

## 步骤 2：西部世界 VPN 代理端口

西部世界通常使用的端口：
- **HTTP 代理**: 7890
- **SOCKS5 代理**: 7891
- **或者**: 10808, 10809

**在 Windows 上确认端口**：
1. 打开西部世界客户端
2. 查看设置 → 本地代理
3. 记下端口号

## 步骤 3：配置 WSL2 代理

### 方法 A：临时设置（推荐先测试）

```bash
# 设置代理（假设端口是 7890）
export http_proxy="http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):7890"
export https_proxy="http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):7890"
export ALL_PROXY="socks5://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):7890"

# 测试连接
curl -I https://www.google.com
```

### 方法 B：永久设置

编辑 `~/.bashrc`：
```bash
nano ~/.bashrc
```

添加以下内容（在文件末尾）：
```bash
# WSL2 代理配置
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export http_proxy="http://${WINDOWS_IP}:7890"
export https_proxy="http://${WINDOWS_IP}:7890"
export ALL_PROXY="socks5://${WINDOWS_IP}:7890"
export no_proxy="localhost,127.0.0.1,::1"

# 快捷命令
alias proxy-on='export http_proxy="http://${WINDOWS_IP}:7890" https_proxy="http://${WINDOWS_IP}:7890" ALL_PROXY="socks5://${WINDOWS_IP}:7890"'
alias proxy-off='unset http_proxy https_proxy ALL_PROXY'
```

然后应用：
```bash
source ~/.bashrc
```

## 步骤 4：允许 WSL2 访问 Windows 代理

### 在 Windows 防火墙中允许：

**方法 1：临时允许（简单）**
```powershell
# 在 Windows PowerShell（管理员）中执行：
New-NetFirewallRule -DisplayName "WSL2 Proxy" -Direction Inbound -LocalPort 7890 -Protocol TCP -Action Allow
```

**方法 2：在西部世界客户端中配置**
1. 打开西部世界设置
2. 找到"允许局域网连接"或"LAN"
3. 启用该选项

## 步骤 5：测试代理

```bash
# 测试 HTTP 代理
curl -I https://www.google.com

# 测试速度
curl -o /dev/null -w "Speed: %{speed_download} bytes/sec\n" https://www.google.com

# 查看 IP（应该显示 VPN 的 IP）
curl https://api.ipify.org
```

## 常见问题

### Q1: 连接被拒绝
**原因**：Windows 防火墙阻止
**解决**：
- 检查西部世界的"允许局域网连接"选项
- 添加防火墙规则（见步骤 4）

### Q2: 代理无效
**原因**：端口不对
**解决**：
- 在 Windows 上确认西部世界的代理端口
- 可能是 7890, 10808, 或其他

### Q3: 有时有效有时无效
**原因**：Windows IP 变化
**解决**：
- 使用动态获取（方法 B）
- 每次启动 WSL2 自动获取新 IP

## 端即用脚本

我为你准备了一个脚本：
