# 协议生成器Web版 - 项目总结

## 项目信息
- **项目名称**：软件著作权合作协议生成器 Web 版
- **位置**：`/mnt/d/桌面/协议生成器Web版/`
- **完成时间**：2026-02-28
- **状态**：✅ 已完成并上线

---

## 技术栈

### 后端
- **框架**：Flask 3.0.0
- **数据库**：SQLite + SQLAlchemy 3.1.1
- **文档处理**：python-docx 1.1.0
- **跨域**：Flask-CORS 4.0.0

### 前端
- **框架**：React 18.2.0
- **UI库**：Ant Design 5.12.0
- **HTTP**：Axios 1.6.0
- **路由**：React Router 6.20.0

---

## 核心功能

### 1. 多软件提取
- 从一个Word文档提取所有软件信息
- 自动识别软件名称、版本、开发日期
- 共享著作权人信息

### 2. 批量生成
- 为每个软件生成独立的协议文档
- 每个文档使用对应的开发日期计算协议日期
- 保留模板格式和样式

### 3. ZIP打包
- 多文件自动打包成ZIP
- 方便一次性下载所有协议

### 4. 前端显示
- 智能识别单软件/多软件
- 多软件时显示列表视图
- 显示所有软件的详细信息

---

## 关键技术要点

### Word文档处理

**问题1：页面格式丢失**
```python
# ❌ 错误：创建新文档
final_doc = Document()

# ✅ 正确：直接修改模板
doc = Document(template_file)
```

**问题2：段落内容被破坏**
```python
# ❌ 错误：整个段落被替换
runs[0].text = new_text

# ✅ 正确：只替换匹配部分
full_text = para.text.replace(old_text, new_text)
runs[0].text = full_text
```

**问题3：Unicode引号不匹配**
```python
# ❌ 错误：无法匹配中文引号
r'["""](.+?)"'

# ✅ 正确：使用Unicode转义
r'[\u201c\u201d"]([^"""]+)[\u201c\u201d"]'
```

### 前端数据结构

**问题：后端返回多软件，前端用单软件字段**
```javascript
// ❌ 错误：旧字段（单软件）
{previewData.software_name}

// ✅ 正确：新字段（多软件）
{previewData.software_list[0].software_name}
```

---

## 项目结构

```
协议生成器Web版/
├── backend/
│   ├── app.py              # Flask主程序
│   ├── models.py           # 数据库模型
│   ├── utils.py            # 核心逻辑（提取、生成）
│   ├── templates/          # 协议模板（2-13方）
│   ├── uploads/            # 上传文件
│   └── outputs/            # 生成的协议
├── frontend/
│   ├── src/
│   │   ├── App.js          # 主应用
│   │   └── pages/
│   │       ├── Home.js     # 主页（上传、生成）
│   │       └── History.js  # 历史记录
│   └── package.json
└── database/
    └── app.db              # SQLite数据库
```

---

## API接口

### 健康检查
```
GET /api/health
```

### 上传预览
```
POST /api/preview
参数: FormData (file: .docx)
返回: {
  software_count: 3,
  software_list: [...],
  owners: [...],
  owners_count: 10
}
```

### 生成协议
```
POST /api/generate
参数: JSON (预览数据)
返回: {
  download_url: "/api/download/xxx.zip",
  software_count: 3,
  is_zip: true
}
```

### 下载文件
```
GET /api/download/<filename>
```

---

## 测试验证

### 测试文件
`光伏建设对草地土壤微环境的影响监测平台.docx`

### 测试结果
- ✅ 提取了 3 个软件
- ✅ 生成了 3 个独立协议文档
- ✅ 打包成 ZIP 文件
- ✅ 所有内容格式正确
- ✅ 前端正确显示所有信息

### 生成的文件
1. `合作协议-光伏建设对草地土壤微环境的影响监测平台.docx`
   - 软件名称：光伏建设对草地土壤微环境的影响监测平台V1.0
   - 协议日期：2025年9月21日

2. `合作协议-草地光伏土壤微生态变化分析平台.docx`
   - 软件名称：草地光伏土壤微生态变化分析平台V1.0
   - 协议日期：2025年9月24日

3. `合作协议-光伏建设草地土壤微环境监测软件.docx`
   - 软件名称：光伏建设草地土壤微环境监测软件V1.0
   - 协议日期：2025年9月28日

---

## 启动方式

### 后端
```bash
cd /mnt/d/桌面/协议生成器Web版/backend
python3 app.py
```
地址：http://localhost:5000

### 前端
```bash
cd /mnt/d/桌面/协议生成器Web版/frontend
npm start
```
地址：http://localhost:3000

---

## 使用流程

1. **上传文档** → 拖拽或点击上传 `.docx` 文件
2. **确认信息** → 查看提取的软件信息和著作权人
3. **生成协议** → 点击"生成协议"按钮
4. **下载文件** → 点击"下载合作协议"（ZIP或单个文件）

---

## 注意事项

1. **强制刷新**：修改前端代码后，需要强制刷新浏览器（Ctrl+Shift+R）
2. **格式保留**：Word文档处理时必须直接修改模板，不能创建新文档
3. **文本替换**：必须保留完整段落文本，只替换匹配部分
4. **Unicode处理**：中文引号需要使用 Unicode 转义序列
5. **数据结构**：前端使用 `software_list` 数组，不是单软件字段

---

## 维护记录

### 2026-02-28
- ✅ 完成多软件提取和生成功能
- ✅ 实现ZIP打包下载
- ✅ 修复前端显示问题（多软件数据结构）
- ✅ 完整测试通过

---

**项目状态：生产就绪 ✅**
