# 配置 Browser 自动化指南

## 前提条件
- ✅ Chrome 浏览器已安装
- ✅ OpenClaw Chrome 扩展已安装
  - 如果没装，访问：https://chrome.google.com/webstore
  - 搜索 "OpenClaw" 并安装

## 步骤 1：启动 Gateway
```bash
# 检查状态
openclaw status

# 如果没运行，启动它
openclaw gateway
```

## 步骤 2：连接 Chrome 标签页

### 方法 A：使用 Chrome 扩展（推荐）
1. 打开 Chrome 浏览器
2. 打开任意网页（比如 https://x.com 或 https://xiaohongshu.com）
3. 点击浏览器右上角的 OpenClaw 扩展图标
4. 扩展会显示 "Connected" 或徽章变绿
5. 现在我可以通过 browser 工具控制这个标签页

### 方法 B：使用 OpenClaw 内置浏览器
```bash
# 启动 OpenClaw 管理的浏览器
openclaw browser start

# 这会打开一个独立的浏览器窗口
# 我可以直接控制这个浏览器
```

## 步骤 3：测试浏览器控制

让我执行测试命令：
```json
{
  "action": "status",
  "profile": "chrome"
}
```

如果成功，我会看到：
- 已连接的标签页列表
- 当前页面信息
- 浏览器状态

## 常见问题

### 问题 1：扩展图标是灰色的
**原因**：Gateway 没运行
**解决**：运行 `openclaw gateway`

### 问题 2：点击扩展没反应
**原因**：扩展未正确安装或权限不足
**解决**：
- 重新安装扩展
- 检查 Chrome 扩展权限设置

### 问题 3：显示 "No tab connected"
**原因**：没有激活标签页
**解决**：
- 确保打开了至少一个标签页
- 点击扩展图标激活当前标签页

## 两种模式对比

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Chrome 扩展 | 使用现有浏览器，cookie/登录状态都在 | 需要手动激活标签页 | 研究已登录的网站（小红书、X） |
| OpenClaw 浏览器 | 完全自动化，无需手动操作 | 独立浏览器，没有登录状态 | 自动化测试、爬虫 |

## 推荐配置（针对我们的项目）

### 研究 Felix 的 X 账号
1. 用 Chrome 打开 https://x.com/FelixCraftAI
2. 登录你的 X 账号
3. 点击 OpenClaw 扩展激活标签页
4. 让我执行：
   - 查看发帖历史
   - 分析互动数据
   - 研究内容策略

### 研究小红书
1. 用 Chrome 打开 https://xiaohongshu.com
2. 登录你的小红书账号
3. 点击扩展激活
4. 让我执行：
   - 搜索相关内容
   - 分析热门笔记
   - 研究用户互动

## 下一步
配置完成后告诉我，我会测试这两个工具，然后开始深度研究！🦞
