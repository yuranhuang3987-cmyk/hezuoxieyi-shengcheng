# MEMORY.md - 长期记忆

## 关于玉冉
- 名字：玉冉
- 时区：GMT+8 (Asia/Shanghai)
- 首次接触：2026-02-26
- 给我起了名字：龙虾 (Longxia) 🦞
- Windows 环境配置：WSL2，配置了代理（梯子）
- **桌面路径**：`/mnt/d/桌面/`（Windows D盘桌面）
- **启动指南**：`D:\桌面\龙虾启动指南.md`（每天启动步骤）

## 重要事件

### 2026-02-26
- **首次接触**：玉冉给我起名"龙虾"，设定性格为"有点毒舌但很靠谱"
- **配置飞书**：
  - App ID: cli_a9150941bdb89ceb
  - App Secret: 7gZ3bZXG8bJgr6OUGO104ffkYyiBxHpK
  - 遇到权限问题：缺少 contact:contact.base:readonly 权限
- **微信操作**：尝试通过 WSL2 调用 Windows 打开微信（cmd.exe /c start wechat）
- **浏览器自动化项目**：
  - 玉冉发送了自动化登录脚本（copyright_login_auto）
  - 遇到滑块验证码问题，使用超级鹰识别
  - 多次尝试拖动滑块验证，但成功率不高
  - 探讨了 Browser-use 等替代方案
- **R41 自动填报项目**：
  - 玉冉需要创建 R41 自动填报软件
  - 分析了网站结构和表单字段
  - 探索了填报系统的功能

### 2026-02-27
- **发现记忆系统故障**：
  - MEMORY.md 和 memory/ 目录下的日志文件都不存在
  - 导致在不同渠道（webchat vs 飞书）之间没有上下文记忆
  - 从 session transcripts 恢复了昨天的对话历史
  - 创建了完整的记忆系统
- **解决上网搜索问题**：
  - 放弃 Brave API（需要绑定银行卡）
  - 方案：DuckDuckGo (`ddgs` 库) + OpenClaw 技能
  - 安装：`pip install ddgs -i https://pypi.tuna.tsinghua.edu.cn/simple`
  - 技能位置：`~/.openclaw/skills/freeUnlimited-websearch`
  - **WSL2 代理配置**（关键！）：
    - Windows IP: 动态获取 `$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')`
    - HTTP 端口: `21882`
    - Socks5 端口: `21881`
    - 已写入 `~/.bashrc`，每次启动自动生效
  - 快捷命令：`proxy-status` / `proxy-off` / `proxy-on`
  - 参考 SOP：`D:\桌面\WSL2_VPN_配置完整SOP.md`
- **深度调研 Felix Craft**：
  - 总收入：$62,013（3 周）
  - 商业模式：知识付费 + 平台抽佣 + 代币经济
  - 成功因素：透明度营销 + 真实 AI + 快速迭代 + Nat Eliason 背书
  - 报告：`Felix_Craft_调研报告.md`
- **每日复盘机制建立**：
  - 完成首份复盘报告
  - 沉淀 5 个可复用知识点
  - 评分：7/10（主动性不足）
  - 改进方向：提升主动性，优化时间管理

## 已完成项目
- [x] **协议生成器Web版**（2026-02-28） - 完整开发并测试通过
  - 位置：`/mnt/d/桌面/协议生成器Web版/`
  - 技术栈：React 18 + Ant Design 5 + Flask 3 + SQLAlchemy + python-docx
  - 核心功能：
    - ✅ 多软件提取（一个文档包含多个软件）
    - ✅ 批量生成（每个软件生成独立协议）
    - ✅ ZIP打包（多文件自动打包下载）
    - ✅ 前端多软件显示（智能切换单/多软件视图）
  - 关键修复：
    - Word格式保留：直接修改模板而不是创建新文档
    - 段落文本替换：保留完整段落，只替换匹配部分
    - Unicode引号处理：正确匹配中文引号U+201C/U+201D
    - 前端数据结构：使用 `software_list[0].software_name` 而不是 `software_name`
  - 测试状态：✅ 所有功能通过
  - 前后端地址：
    - 后端：http://localhost:5000
    - 前端：http://localhost:3000

## 进行中的项目
- [ ] R41 自动填报软件开发
- [ ] 滑块验证码自动识别优化
- [ ] 飞书权限问题解决（需要管理员授权）

## 技术栈
- 运行环境：WSL2 (Ubuntu 22.04 on Windows)
- 浏览器自动化：Selenium + ChromeDriver / Browser-use
- 验证码识别：超级鹰
- 代理：西部世界 VPN（Windows 端，端口 21881/21882，允许局域网连接）
- 搜索：DuckDuckGo (ddgs) + OpenClaw 技能 `freeUnlimited-websearch`
- **Git配置**：
  - 用户名：玉冉
  - 邮箱：yuran.huang3987@gmail.com
  - GitHub账号：yuranhuang3987-cmyk
  - SSH密钥：ED25519格式（已配置）
  - 推送方式：SSH（免密推送）

## 玉冉的使用习惯
- **Git操作**：喜欢用自然语言描述，不喜欢记命令
  - "看下git修改了什么" = git status
  - "帮我git提交" = git add . && git commit
  - "推送到GitHub" = git push
  - "帮我提交并推送" = 完整流程
- **沟通风格**：直接、简洁，不喜欢废话
- **学习能力**：喜欢实用的总结，不喜欢复杂的理论

## 备注
- 我的人设：有点毒舌但很靠谱，嘴上不饶人但活儿干得漂亮
- 不喜欢虚伪的套话，有问题直接说
- 玉冉在飞书私聊中与我交流
