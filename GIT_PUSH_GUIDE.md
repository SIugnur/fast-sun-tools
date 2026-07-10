# FastSunTools - Git 上传指南

## 首次上传到 GitHub

### 步骤 1：安装 Git
如果还没有安装 Git，请下载并安装：
- Windows: https://git-scm.com/download/win
- 安装时选择 "Use Git from Bash only" 和 "Checkout Windows-style"

### 步骤 2：在项目目录打开 Git Bash
打开项目文件夹，右键选择 "Git Bash Here"，然后依次执行以下命令：

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交代码
git commit -m "Initial commit: FastSunTools v1.0.0

功能特性：
- 窗口置顶功能
- 文件浏览器（支持多种文件预览）
- OCR 屏幕文本提取
- 图片转PDF工具
- PDF/Word/Excel/PPT 预览"

# 4. 添加远程仓库
git remote add origin https://github.com/SIugnur/fast-sun-tools.git

# 5. 推送到 GitHub（首次推送需要输入用户名和Token）
git push -u origin master
```

### 注意：
- 推送时需要使用 **GitHub Personal Access Token** 作为密码，而不是登录密码
- Token 获取方式：GitHub -> Settings -> Developer settings -> Personal access tokens -> Generate new token

## 以后更新代码

```bash
git add .
git commit -m "你的更新说明"
git push
```

## 注意事项

1. **不要上传的文件**：
   - `dist/` 文件夹（包含编译后的可执行文件，太大）
   - `__pycache__/` 文件夹
   - `build/` 文件夹
   - `.gitignore` 中已排除的文件

2. **敏感信息**：
   - 不要上传包含密码或密钥的文件
   - 使用环境变量代替硬编码的密钥

3. **提交规范**：
   - 提交信息要清晰描述改动
   - 小步提交，不要一次性提交大量不相关的改动
