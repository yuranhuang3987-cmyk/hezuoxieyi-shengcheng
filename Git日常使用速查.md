# Git 日常使用速查表（小白版）

## 🎯 你只需要记住这5个命令

### 1️⃣ 查看状态（最常用）
```bash
git status
```
**作用**：看看哪些文件被修改了
**什么时候用**：随时都可以用，了解当前状态

---

### 2️⃣ 添加修改
```bash
git add .
```
**作用**：把所有修改的文件加入"准备提交"列表
**什么时候用**：修改完代码，准备提交前

---

### 3️⃣ 提交
```bash
git commit -m "写了什么修改"
```
**作用**：保存这次的修改
**什么时候用**：完成一个小功能，或修复了一个bug

**示例**：
```bash
git commit -m "修复了登录页面的bug"
git commit -m "添加了用户注册功能"
git commit -m "更新了README文档"
```

---

### 4️⃣ 推送到远程（如果有GitHub/GitLab）
```bash
git push
```
**作用**：把你的代码上传到 GitHub/GitLab
**什么时候用**：提交后，想备份到云端

---

### 5️⃣ 拉取更新（如果有GitHub/GitLab）
```bash
git pull
```
**作用**：从 GitHub/GitLab 下载最新代码
**什么时候用**：开始工作前，或别人更新了代码

---

## 📝 日常工作流程

### 场景1：修改代码并保存
```bash
# 1. 修改了文件（在编辑器里改代码）
# ...

# 2. 查看改了什么
git status

# 3. 添加修改
git add .

# 4. 提交
git commit -m "修改说明"

# 5. （可选）推送到GitHub
git push
```

### 场景2：每天开始工作
```bash
# 1. 拉取最新代码
git pull

# 2. 开始工作...
```

### 场景3：每天结束工作
```bash
# 1. 查看状态
git status

# 2. 添加修改
git add .

# 3. 提交
git commit -m "今天的修改"

# 4. 推送
git push
```

---

## 🆘 常见问题

### Q1: 我改错了文件，想恢复怎么办？
```bash
# 查看状态，确认文件名
git status

# 恢复单个文件（撤销修改）
git restore 文件名

# 或者（旧命令）
git checkout -- 文件名
```

### Q2: 我想看看之前的提交记录
```bash
# 查看历史
git log

# 简洁模式（推荐）
git log --oneline

# 只看最近5次
git log --oneline -5
```

### Q3: 提交信息写错了，想改一下
```bash
# 修改最后一次提交的信息
git commit --amend -m "新的提交信息"
```

### Q4: 我想撤销刚才的提交（还没push）
```bash
# 撤销提交，但保留修改
git reset --soft HEAD~1

# 撤销提交，丢弃修改（危险！）
git reset --hard HEAD~1
```

### Q5: 不小心把不该提交的文件提交了
```bash
# 从Git中移除，但保留本地文件
git rm --cached 文件名

# 然后提交这个移除操作
git commit -m "移除敏感文件"
```

---

## ⚠️ 注意事项

### ✅ 好习惯
- 每完成一个小功能就提交一次
- 提交信息写清楚做了什么
- 每天下班前 push 代码
- 重要修改前先 pull 最新代码

### ❌ 坏习惯
- 一次性提交很多修改
- 提交信息写"修改"、"更新"（太模糊）
- 很久才 push 一次
- 不看状态就直接提交

---

## 📚 提交信息规范（简单版）

### 格式
```bash
git commit -m "类型: 具体说明"
```

### 常用类型
- `feat:` 新功能
- `fix:` 修复bug
- `update:` 更新功能
- `docs:` 文档修改
- `style:` 代码格式调整

### 示例
```bash
git commit -m "feat: 添加用户登录功能"
git commit -m "fix: 修复登录页面样式错误"
git commit -m "docs: 更新README"
git commit -m "style: 调整代码缩进"
```

---

## 🎓 进阶（暂时不用记）

### 分支（以后学）
```bash
git branch 分支名        # 创建分支
git checkout 分支名      # 切换分支
git checkout -b 分支名   # 创建并切换
git merge 分支名         # 合并分支
```

### 暂存工作（临时保存）
```bash
git stash              # 暂存当前修改
git stash pop          # 恢复暂存的修改
```

---

## 🔍 快速检查清单

### 每天开始工作
- [ ] `git pull` 拉取最新代码

### 每次提交前
- [ ] `git status` 查看修改
- [ ] `git add .` 添加修改
- [ ] `git commit -m "说明"` 提交

### 每天结束工作
- [ ] `git status` 确认都提交了
- [ ] `git push` 推送到远程

---

## 💡 记忆口诀

**一看二加三提交，最后push没问题**

1. **看**：`git status`
2. **加**：`git add .`
3. **提交**：`git commit -m "说明"`
4. **推送**：`git push`

---

## 📞 遇到问题怎么办？

1. **先看状态**：`git status`
2. **看历史**：`git log --oneline`
3. **问龙虾**：直接问我，我帮你解决！

---

**记住：Git 不难，多用就熟了！** 🦞
