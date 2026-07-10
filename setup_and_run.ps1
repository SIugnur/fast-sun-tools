# FastSunTools - 一键安装和运行脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FastSunTools - 安装和启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check and Install Python
Write-Host "[1/3] 检查 Python..." -ForegroundColor Cyan
$pythonInstalled = $false

if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Python 已安装: $(python --version)" -ForegroundColor Green
    $pythonInstalled = $true
} else {
    Write-Host "正在安装 Python 3.11..." -ForegroundColor Yellow
    
    $arch = $env:PROCESSOR_ARCHITECTURE
    if ($arch -eq "AMD64") {
        $installerUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
        $installerName = "python-3.11.5-amd64.exe"
    } else {
        $installerUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5.exe"
        $installerName = "python-3.11.5.exe"
    }
    
    $installerPath = "$env:TEMP\$installerName"
    
    try {
        Write-Host "正在下载 Python 安装包..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        
        if (Test-Path $installerPath) {
            Write-Host "正在安装 Python（可能需要几分钟）..." -ForegroundColor Gray
            $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -PassThru
            
            if ($process.ExitCode -eq 0 -or (Test-Path "C:\Program Files\Python311\python.exe") -or (Test-Path "C:\Python311\python.exe")) {
                Write-Host "Python 安装成功！" -ForegroundColor Green
                $pythonInstalled = $true
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            }
        }
    } catch {
        Write-Host "Python 安装失败: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Step 2: Install Python Dependencies
Write-Host "[2/3] 安装 Python 依赖..." -ForegroundColor Cyan

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Start-Sleep -Seconds 2

if ($pythonInstalled) {
    try {
        $pythonCmd = "python"
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
            $possiblePaths = @(
                "C:\Program Files\Python311\python.exe",
                "C:\Python311\python.exe",
                "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe"
            )
            
            foreach ($path in $possiblePaths) {
                if (Test-Path $path) {
                    $pythonCmd = $path
                    break
                }
            }
        }
        
        Write-Host "正在安装依赖包 (PyQt5, Pillow, mss, etc.)..." -ForegroundColor Gray
        Write-Host "请耐心等待..." -ForegroundColor Gray
        
        & $pythonCmd -m pip install --upgrade pip --quiet
        & $pythonCmd -m pip install PyQt5==5.15.10 PyQt5-sip==12.13.0 Pillow==10.3.0 mss==9.0.1 pyperclip==1.8.2 PyPDF2==3.0.1 python-docx==1.1.0 openpyxl==3.1.2 python-pptx==0.6.23 PyMuPDF==1.28.0 opencv-python-headless==5.0.0.93 numpy==1.26.4 --quiet
        
        Write-Host "依赖安装成功！" -ForegroundColor Green
    } catch {
        Write-Host "依赖安装失败: $_" -ForegroundColor Red
        Write-Host "可以手动运行: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "无法安装依赖 - Python 未安装" -ForegroundColor Red
}

Write-Host ""

# Step 3: Launch Application
Write-Host "[3/3] 启动 FastSunTools..." -ForegroundColor Cyan

if ($pythonInstalled) {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Start-Sleep -Seconds 2
    
    try {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "FastSunTools 正在启动..." -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        
        python main.py
    } catch {
        Write-Host "启动失败: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "手动运行:" -ForegroundColor Yellow
        Write-Host "  python main.py" -ForegroundColor Gray
    }
} else {
    Write-Host "无法启动应用 - Python 未安装" -ForegroundColor Red
}
