# FastSunTools 发布指南

## 快速打包

运行 `build.bat` 脚本即可自动完成打包。

打包后的文件位于 `dist/FastSunTools/` 目录。

## 打包说明

### 环境要求
- Windows 10/11
- Python 3.8+ (已包含在打包中)

### 包含的文件
打包后会生成一个文件夹，包含：
- `FastSunTools.exe` - 主程序
- 所有依赖库
- 运行时文件

### 分发方式

#### 方式1：直接分发文件夹
将 `dist/FastSunTools/` 文件夹压缩或直接复制给用户。

#### 方式2：创建安装包
可以使用以下工具创建安装程序：
- Inno Setup
- NSIS
- WiX Toolset

### 依赖项
所有依赖已打包，无需用户安装 Python 或其他库。

### 注意事项
- 确保 Tesseract OCR 已安装在用户电脑上（如需 OCR 功能）
- 首次运行可能需要管理员权限
- 某些杀毒软件可能会误报，请添加到白名单
