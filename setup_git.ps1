# FastSunTools - Git 初始化和上传脚本

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FastSunTools - Git 上传到 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
Write-Host "[1/5] 检查 Git 安装..." -ForegroundColor Yellow
$gitCmd = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitCmd) {
    Write-Host "Git 未安装！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装 Git：" -ForegroundColor Yellow
    Write-Host "1. 访问 https://git-scm.com/download/win" -ForegroundColor Gray
    Write-Host "2. 下载并安装 Git for Windows" -ForegroundColor Gray
    Write-Host "3. 安装时选择 'Use Git from Bash only'" -ForegroundColor Gray
    Write-Host "4. 重新打开此窗口" -ForegroundColor Gray
    Write-Host ""
    
    # 打开下载页面
    Start-Process "https://git-scm.com/download/win"
    
    pause
    exit 1
}

Write-Host "Git 已安装: $($gitCmd.Source)" -ForegroundColor Green
Write-Host ""

# 配置 Git 用户信息
Write-Host "[2/5] 配置 Git 用户信息..." -ForegroundColor Yellow
Write-Host "请输入你的 GitHub 用户名：" -ForegroundColor Cyan
$githubUsername = Read-Host
Write-Host "请输入你的 GitHub Personal Access Token：" -ForegroundColor Cyan
Write-Host "（Token 不会显示，输入时直接粘贴即可）" -ForegroundColor Gray
$githubToken = Read-Host -AsSecureString
$githubToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($githubToken))

# 设置 Git 用户名和邮箱
Write-Host "正在配置 Git..." -ForegroundColor Gray
git config --global user.name $githubUsername
git config --global user.email "$githubUsername@users.noreply.github.com"

Write-Host "Git 配置完成！" -ForegroundColor Green
Write-Host ""

# 初始化仓库
Write-Host "[3/5] 初始化 Git 仓库..." -ForegroundColor Yellow

# 检查是否已有 .git 目录
if (Test-Path ".git") {
    Write-Host "Git 仓库已存在，跳过初始化" -ForegroundColor Gray
} else {
    Write-Host "正在初始化仓库..." -ForegroundColor Gray
    git init
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git 初始化失败！" -ForegroundColor Red
        pause
        exit 1
    }
    
    Write-Host "Git 仓库初始化成功！" -ForegroundColor Green
}

Write-Host ""

# 添加远程仓库
Write-Host "[4/5] 配置远程仓库..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/SIugnur/fast-sun-tools.git"

# 检查是否已有 remote
$currentRemote = git remote get-url origin 2>$null

if ($currentRemote) {
    Write-Host "远程仓库已配置: $currentRemote" -ForegroundColor Gray
    if ($currentRemote -ne $remoteUrl) {
        Write-Host "更新远程仓库地址..." -ForegroundColor Gray
        git remote set-url origin $remoteUrl
    }
} else {
    Write-Host "添加远程仓库..." -ForegroundColor Gray
    git remote add origin $remoteUrl
}

Write-Host "远程仓库配置完成！" -ForegroundColor Green
Write-Host ""

# 推送到 GitHub
Write-Host "[5/5] 推送到 GitHub..." -ForegroundColor Yellow

# 设置远程仓库认证
git remote set-url origin "https://$githubUsername`:$githubToken@github.com/SIugnur/fast-sun-tools.git"

# 添加所有文件（排除 .gitignore 中的文件）
Write-Host "添加文件..." -ForegroundColor Gray
git add .

# 检查是否有文件要提交
$status = git status --porcelain
if ($status.Count -eq 0) {
    Write-Host "没有新文件需要提交" -ForegroundColor Yellow
} else {
    # 提交代码
    Write-Host "提交代码..." -ForegroundColor Gray
    $commitMessage = @"
Initial commit: FastSunTools v1.0.0

功能特性：
- 窗口置顶功能
- 文件浏览器（支持多种文件预览）
- OCR 屏幕文本提取
- 图片转PDF工具
- PDF/Word/Excel/PPT 预览
"@
    
    git commit -m $commitMessage
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "提交失败！" -ForegroundColor Red
        pause
        exit 1
    }
    
    Write-Host "代码提交成功！" -ForegroundColor Green
}

# 推送到 GitHub
Write-Host "正在推送到 GitHub..." -ForegroundColor Gray
Write-Host "（这可能需要几分钟，请耐心等待）" -ForegroundColor Gray
Write-Host ""

git push -u origin master --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ 成功推送到 GitHub！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "仓库地址：" -ForegroundColor Cyan
    Write-Host "https://github.com/SIugnur/fast-sun-tools" -ForegroundColor White
    Write-Host ""
    
    # 打开仓库页面
    Start-Process "https://github.com/SIugnur/fast-sun-tools"
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ 推送失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "1. Token 无效或已过期" -ForegroundColor Gray
    Write-Host "2. 仓库不存在或没有推送权限" -ForegroundColor Gray
    Write-Host "3. 网络连接问题" -ForegroundColor Gray
    Write-Host ""
    Write-Host "请检查后重试！" -ForegroundColor Yellow
}

Write-Host ""
pause
