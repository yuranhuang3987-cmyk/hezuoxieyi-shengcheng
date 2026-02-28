# 西部世界 VPN - 允许局域网连接配置

## 已知信息
- ✅ Windows IP: 172.29.160.1
- ✅ Socks5 端口: 21881
- ✅ HTTP 端口: 21882
- ✅ PAC 端口: 21883
- ❌ 无法连接到这些端口

## 问题原因
西部世界 VPN **没有启用"允许局域网连接"**

## 解决步骤

### 方法 1：在西部世界客户端中启用（推荐）

1. **打开西部世界客户端**
2. **找到设置**（可能在右上角或左下角）
3. **查找以下选项之一**：
   - "允许局域网连接"
   - "Allow LAN"
   - "局域网共享"
   - "允许来自局域网的连接"
   - 在"网络设置"或"高级设置"中

4. **启用该选项**
5. **重启西部世界**（如果需要）

### 方法 2：检查 Windows 防火墙

即使启用了"允许局域网连接"，防火墙可能还是阻止。

**在 Windows PowerShell（管理员）中执行**：
```powershell
# 允许 HTTP 端口
New-NetFirewallRule -DisplayName "西部世界 HTTP" -Direction Inbound -LocalPort 21882 -Protocol TCP -Action Allow

# 允许 Socks5 端口
New-NetFirewallRule -DisplayName "西部世界 Socks5" -Direction Inbound -LocalPort 21881 -Protocol TCP -Action Allow
```

### 方法 3：临时关闭防火墙（测试用）

**仅用于测试**，确认后记得重新开启：
```powershell
# 关闭防火墙（测试）
Set-NetFirewallProfile -Profile Public,Private -Enabled False

# 测试完后重新开启
Set-NetFirewallProfile -Profile Public,Private -Enabled True
```

## 验证步骤

启用后，在 WSL2 中测试：
```bash
# 测试端口连接
nc -zv 172.29.160.1 21882

# 测试 HTTP 代理
curl -x http://172.29.160.1:21882 -I https://www.google.com

# 查看 IP
curl -x http://172.29.160.1:21882 https://api.ipify.org
```

## 配置完成后

告诉我"已启用"，我会：
1. 配置 WSL2 代理
2. 加速 Chromium 下载
3. 测试搜索功能

---

**现在去西部世界客户端启用"允许局域网连接"吧！** 🦞
