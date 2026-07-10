# FastSunTools - 桌面办公助手

## 功能特性

- **窗口置顶**：将应用程序固定在其他窗口上方
- **文件浏览器**：支持多种文件类型的预览和缩略图显示
  - 图片预览（JPG, PNG, GIF, BMP, WebP, TIFF）
  - 文本预览（TXT, PY, JS, HTML, CSS, JSON, XML, MD）
  - PDF 预览（支持图片型和文本型 PDF）
  - Word 文档预览（.docx, .doc）
  - Excel 预览（.xlsx, .xls）
  - PowerPoint 预览（.pptx, .ppt）
- **屏幕截图**：快速截取屏幕选定区域
- **图片转PDF**：将多张图片拼接成一个PDF文件
- **排序功能**：支持按名称、时间、大小、类型排序
- **视图切换**：支持缩略图和列表两种视图模式

## 安装

### 环境要求
- Windows 10/11
- Python 3.8+（仅开发环境需要）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/SIugnur/fast-sun-tools.git
cd fast-sun-tools
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行应用**
```bash
python main.py
```

## 打包发布

运行打包脚本：
```bash
python build_app.py
```

打包后的文件位于 `dist/FastSunTools/` 目录。

## 使用说明

### 快捷键
- `Ctrl + T` - 切换窗口置顶
- `Ctrl + F` - 搜索文件
- `Ctrl + R` - 刷新目录
- `Ctrl + H` - 主目录
- `Alt + O` - 屏幕截图
- `Esc` - 关闭应用

### 图片转PDF使用
1. 点击「图片转PDF」按钮
2. 添加图片（支持拖拽调整顺序）
3. 选择输出质量和方向
4. 点击「开始转换PDF」

## 开发

### 项目结构
```
FastSunTools/
├── main.py                  # 应用入口
├── requirements.txt         # 依赖列表
├── src/
│   ├── main_window.py      # 主窗口
│   ├── file_explorer/       # 文件浏览器模块
│   ├── ocr/                 # 截图模块
│   └── image_to_pdf/        # 图片转PDF模块
└── dist/                    # 打包输出目录
```

### 技术栈
- **GUI 框架**：PyQt5
- **PDF 处理**：PyMuPDF, PyPDF2
- **文档处理**：python-docx, openpyxl, python-pptx
- **图像处理**：Pillow
- **屏幕捕获**：mss

## Git 上传指南

### 首次上传
```bash
# 1. 初始化仓库
git init

# 2. 添加文件
git add .

# 3. 提交
git commit -m "Initial commit: FastSunTools v1.0.0"

# 4. 添加远程仓库
git remote add origin https://github.com/SIugnur/fast-sun-tools.git

# 5. 推送
git push -u origin master
```

### 更新代码
```bash
git add .
git commit -m "Your update message"
git push
```

## 许可证

MIT License

## 作者

FastSun Team

## 联系方式

- GitHub: https://github.com/SIugnur/fast-sun-tools
