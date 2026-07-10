# FastSunTools - Python 自动安装脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FastSunTools - Python 安装程序" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装 Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    Write-Host "✓ Python 已安装: $($pythonCmd.Source)" -ForegroundColor Green
    Write-Host "版本: $(python --version)" -ForegroundColor Green
    exit 0
}

Write-Host "正在检查系统环境..." -ForegroundColor Yellow

# 检测系统架构
$arch = $env:PROCESSOR_ARCHITECTURE
if ($arch -eq "AMD64") {
    $installerUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
    $installerName = "python-3.11.5-amd64.exe"
} else {
    $installerUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5.exe"
    $installerName = "python-3.11.5.exe"
}

$installerPath = "$env:TEMP\$installerName"

Write-Host "下载 Python 3.11.5..." -ForegroundColor Yellow
Write-Host "URL: $installerUrl" -ForegroundColor Gray

try {
    # 下载安装程序
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    
    if (Test-Path $installerPath) {
        Write-Host "✓ 下载完成！" -ForegroundColor Green
        
        # 安装 Python（静默安装，添加到 PATH）
        Write-Host ""
        Write-Host "正在安装 Python..." -ForegroundColor Yellow
        Write-Host "（安装过程可能需要几分钟，请耐心等待）" -ForegroundColor Gray
        
        $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host ""
            Write-Host "✓ Python 安装成功！" -ForegroundColor Green
            
            # 刷新环境变量
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            Start-Sleep -Seconds 2
            
            # 验证安装
            if (Get-Command python -ErrorAction SilentlyContinue) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Cyan
                Write-Host "Python 验证：" -ForegroundColor Cyan
                python --version
                Write-Host "✓ Python 安装验证通过！" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Cyan
                
                # 升级 pip
                Write-Host ""
                Write-Host "正在升级 pip..." -ForegroundColor Yellow
                python -m pip install --upgrade pip --quiet
                Write-Host "✓ pip 升级完成！" -ForegroundColor Green
                
                exit 0
            } else {
                Write-Host "⚠ 安装完成但无法立即使用，请重启终端后运行 python --version 验证" -ForegroundColor Yellow
                exit 0
            }
        } else {
            Write-Host "✗ Python 安装失败（错误代码：$($process.ExitCode)）" -ForegroundColor Red
            Write-Host "请手动下载安装：https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "✗ 下载失败" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 安装过程中出现错误：$_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载安装：" -ForegroundColor Yellow
    Write-Host "1. 访问 https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host "2. 下载 Python 3.11 或更高版本" -ForegroundColor Gray
    Write-Host "3. 运行安装程序，勾选 'Add Python to PATH'" -ForegroundColor Gray
    exit 1
}
