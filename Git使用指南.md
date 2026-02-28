# Git 使用指南

## 一、基本概念

### 1. 什么是Git？
Git 是一个分布式版本控制系统，用于跟踪文件的修改历史，方便团队协作。

### 2. 三个区域
- **工作区（Working Directory）**：你编辑文件的地方
- **暂存区（Staging Area）**：准备提交的文件
- **仓库（Repository）**：已提交的历史记录

### 3. 工作流程
```
工作区 → git add → 暂存区 → git commit → 仓库
```

---

## 二、安装和配置

### 1. 安装Git
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install git

# 验证安装
git --version
```

### 2. 初次配置
```bash
# 设置用户名和邮箱（必须）
git config --global user.name "你的名字"
git config --global user.email "your.email@example.com"

# 查看配置
git config --list

# 设置默认编辑器（可选）
git config --global core.editor "code --wait"  # VS Code
```

---

## 三、常用命令

### 1. 创建仓库

**初始化新仓库**
```bash
# 在当前目录创建
git init

# 克隆远程仓库
git clone https://github.com/username/repo.git
git clone git@github.com:username/repo.git  # SSH方式
```

### 2. 日常操作

**查看状态**
```bash
git status              # 查看工作区状态
git status -s           # 简洁模式
```

**添加文件到暂存区**
```bash
git add filename        # 添加单个文件
git add .               # 添加所有修改
git add *.py            # 添加所有.py文件
git add src/            # 添加src目录
```

**提交更改**
```bash
git commit -m "提交说明"              # 提交暂存区的文件
git commit -am "提交说明"             # 跳过暂存，直接提交（仅限已跟踪文件）
git commit --amend -m "新的提交说明"  # 修改最后一次提交
```

**查看历史**
```bash
git log                 # 查看提交历史
git log --oneline       # 简洁模式
git log --graph         # 图形化显示
git log -5              # 查看最近5次提交
```

**查看差异**
```bash
git diff                # 工作区 vs 暂存区
git diff --staged       # 暂存区 vs 最新提交
git diff HEAD           # 工作区 vs 最新提交
```

### 3. 撤销操作

**撤销工作区修改**
```bash
git checkout -- filename    # 撤销文件修改（危险操作）
git restore filename        # Git 2.23+ 推荐方式
```

**撤销暂存**
```bash
git reset HEAD filename     # 取消暂存
git restore --staged filename  # Git 2.23+ 推荐方式
```

**撤销提交**
```bash
git reset --soft HEAD~1     # 撤销提交，保留修改
git reset --hard HEAD~1     # 撤销提交，丢弃修改（危险）
```

### 4. 分支操作

**创建和切换分支**
```bash
git branch                  # 查看本地分支
git branch feature-login    # 创建分支
git checkout feature-login  # 切换分支
git checkout -b feature-login  # 创建并切换（推荐）
git switch feature-login    # Git 2.23+ 切换分支
git switch -c feature-login # Git 2.23+ 创建并切换
```

**合并分支**
```bash
git checkout main           # 切换到目标分支
git merge feature-login     # 合并分支
git merge --no-ff feature-login  # 禁用快进合并（保留分支历史）
```

**删除分支**
```bash
git branch -d feature-login # 删除已合并的分支
git branch -D feature-login # 强制删除分支
```

### 5. 远程仓库

**管理远程仓库**
```bash
git remote -v                           # 查看远程仓库
git remote add origin <url>             # 添加远程仓库
git remote set-url origin <new-url>     # 修改远程地址
git remote remove origin                # 删除远程仓库
```

**推送和拉取**
```bash
git push origin main        # 推送到远程
git push -u origin main     # 首次推送（设置上游分支）
git push                    # 后续推送（简写）

git pull origin main        # 拉取并合并
git pull                    # 简写（需设置上游分支）

git fetch origin            # 只拉取，不合并
```

---

## 四、常见场景

### 场景1：开始新项目
```bash
# 创建项目目录
mkdir my-project
cd my-project

# 初始化Git
git init

# 创建文件
echo "# My Project" > README.md

# 添加并提交
git add README.md
git commit -m "Initial commit"

# 连接远程仓库
git remote add origin https://github.com/username/my-project.git
git push -u origin main
```

### 场景2：修复Bug
```bash
# 从main创建bugfix分支
git checkout main
git checkout -b bugfix-login-error

# 修改代码...
git add .
git commit -m "Fix: login error when password is empty"

# 切回main并合并
git checkout main
git merge bugfix-login-error

# 推送到远程
git push origin main

# 删除bugfix分支
git branch -d bugfix-login-error
```

### 场景3：新功能开发
```bash
# 创建feature分支
git checkout -b feature-user-profile

# 开发过程中多次提交
git add .
git commit -m "Add user profile page"
git add .
git commit -m "Add avatar upload"
git add .
git commit -m "Add profile edit form"

# 合并到main
git checkout main
git merge --no-ff feature-user-profile

# 推送
git push origin main
```

### 场景4：暂存当前工作
```bash
# 正在开发新功能，突然需要修复紧急Bug
git stash                  # 暂存当前修改
git stash save "开发到一半" # 带说明的暂存

# 切换到Bug修复
git checkout -b hotfix-xxx
# ... 修复Bug ...

# 回到之前的工作
git checkout feature-xxx
git stash pop              # 恢复暂存的修改
```

### 场景5：撤销错误的提交
```bash
# 提交后发现有问题
git reset --soft HEAD~1    # 撤销提交，保留修改

# 修改后重新提交
git add .
git commit -m "Correct commit message"
```

---

## 五、.gitignore 文件

### 作用
告诉Git哪些文件/目录不需要跟踪

### 常见配置
```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
env/
*.egg-info/

# Node.js
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# 操作系统
.DS_Store
Thumbs.db

# 敏感文件
.env
config.local
*.key
*.pem
```

### 使用方法
```bash
# 创建.gitignore文件
touch .gitignore

# 如果文件已被跟踪，需要先移除
git rm --cached filename
git rm -r --cached directory/
```

---

## 六、最佳实践

### 1. 提交信息规范
```bash
# 格式：<type>: <subject>

feat: 添加用户登录功能
fix: 修复登录页面样式错误
docs: 更新README文档
style: 代码格式调整（不影响功能）
refactor: 重构用户模块
test: 添加登录测试用例
chore: 更新构建配置
```

### 2. 分支命名规范
```bash
main/master      # 主分支（生产环境）
develop          # 开发分支
feature/xxx      # 新功能分支
bugfix/xxx       # Bug修复分支
hotfix/xxx       # 紧急修复分支
release/xxx      # 发布分支
```

### 3. 提交频率
- ✅ 每完成一个小功能就提交
- ✅ 提交前先测试
- ✅ 确保每次提交都是独立的、完整的
- ❌ 不要一次性提交大量修改

### 4. 推送频率
- ✅ 每天至少推送一次
- ✅ 重要提交立即推送
- ✅ 下班前推送所有更改

### 5. 分支策略
```bash
# 简单项目
main → feature → main

# 团队协作
main → develop → feature → develop → main
```

---

## 七、常见问题

### 1. 忘记切换分支就修改了代码
```bash
# 如果还没提交
git stash                  # 暂存修改
git checkout -b new-branch # 创建新分支
git stash pop              # 恢复修改

# 如果已经提交
git checkout -b new-branch  # 创建新分支（会带走提交）
git checkout main           # 切回原分支
git reset --hard HEAD~1     # 撤销原分支的提交
```

### 2. 合并冲突
```bash
# Git会标记冲突的文件
<<<<<<< HEAD
当前分支的代码
=======
要合并分支的代码
>>>>>>> feature-branch

# 手动解决冲突后
git add conflicted-file
git commit -m "Merge branch 'feature-branch'"
```

### 3. 不小心删除了分支
```bash
# 查看操作历史
git reflog

# 恢复分支
git checkout -b branch-name <commit-hash>
```

### 4. 提交了敏感信息
```bash
# 从历史中完全删除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive-file" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（危险操作）
git push origin --force --all
```

---

## 八、GitHub/GitLab 使用

### 1. SSH密钥配置
```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"

# 查看公钥
cat ~/.ssh/id_rsa.pub

# 复制公钥到GitHub/GitLab
# Settings → SSH and GPG keys → New SSH key

# 测试连接
ssh -T git@github.com
```

### 2. Pull Request（PR）
```bash
# 1. Fork项目
# 2. Clone你的Fork
git clone https://github.com/your-username/project.git

# 3. 创建分支
git checkout -b feature-xxx

# 4. 修改并提交
git add .
git commit -m "Add feature xxx"
git push origin feature-xxx

# 5. 在GitHub/GitLab上创建PR
```

---

## 九、常用命令速查表

| 操作 | 命令 |
|------|------|
| 初始化仓库 | `git init` |
| 克隆仓库 | `git clone <url>` |
| 查看状态 | `git status` |
| 添加文件 | `git add <file>` |
| 提交更改 | `git commit -m "message"` |
| 查看历史 | `git log` |
| 查看差异 | `git diff` |
| 创建分支 | `git branch <name>` |
| 切换分支 | `git checkout <name>` |
| 合并分支 | `git merge <name>` |
| 推送 | `git push origin <branch>` |
| 拉取 | `git pull origin <branch>` |
| 暂存修改 | `git stash` |
| 恢复暂存 | `git stash pop` |

---

## 十、学习资源

### 官方文档
- [Git官网](https://git-scm.com/)
- [Pro Git电子书](https://git-scm.com/book/zh/v2)

### 在线练习
- [Learn Git Branching](https://learngitbranching.js.org/)
- [GitHub Skills](https://skills.github.com/)

### 可视化工具
- **GitKraken** - 跨平台GUI
- **SourceTree** - 免费，功能强大
- **GitHub Desktop** - GitHub官方
- **VS Code Git插件** - 轻量级

---

**提示：** Git是需要实践的工具，多使用才能熟练！
