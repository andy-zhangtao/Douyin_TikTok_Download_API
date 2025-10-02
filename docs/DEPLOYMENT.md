# 部署说明

## 服务器部署步骤

### 1. 安装依赖

确保服务器已安装所有必需的Python包：

```bash
pip3 install -r requirements.txt
```

**关键依赖：**
- `markdown` - 用于渲染文档（已包含在 requirements.txt 第209行）
- `fastapi` - Web框架
- `pywebio` - Web界面

### 2. 确认markdown库已安装

```bash
pip3 show markdown
```

如果未安装，单独安装：

```bash
pip3 install markdown
```

### 3. 启动服务

```bash
# 启动主服务
python3 start.py
```

服务将在配置的端口启动（默认见 config.yaml）。

### 4. 验证文档功能

访问以下URL验证文档路由是否正常：

```
http://你的域名/help
```

应该看到完整的QQ音乐Cookie获取教程。

## 功能说明

### 新增功能

1. **文档路由** - `/help`
   - 自动将 `docs/qqmusic-cookie-guide.md` 转换为HTML
   - 精美的样式和排版
   - 支持表格、代码高亮、引用等Markdown语法

2. **首页入口**
   - 在主页显眼位置显示教程链接
   - 点击后新标签页打开
   - 中英文双语支持

## 故障排查

### ModuleNotFoundError: No module named 'markdown'

**解决方案：**

```bash
# 方案1：重新安装依赖
pip3 install -r requirements.txt

# 方案2：单独安装markdown
pip3 install markdown

# 方案3：指定版本安装
pip3 install Markdown==3.5.2
```

### 文档显示404

**检查：**
1. 确认 `docs/qqmusic-cookie-guide.md` 文件存在
2. 检查文件路径是否正确
3. 确认markdown库已安装

### 文档样式异常

**可能原因：**
- markdown扩展未正确加载
- CSS样式被覆盖

**解决：**
检查 `app/main.py` 中的markdown配置：
```python
html_body = markdown.markdown(
    md_content,
    extensions=['tables', 'fenced_code', 'nl2br', 'toc']
)
```

## 更新日志

### v1.0.0 (2025-01-02)
- ✅ 添加QQ音乐Cookie获取教程文档
- ✅ 实现文档路由 `/help`
- ✅ 在主页添加显眼的教程入口
- ✅ 支持中英文双语
