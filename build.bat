@echo off
chcp 65001 >nul
echo ========================================
echo FastSunTools 打包工具
echo ========================================
echo.

echo [1/3] 清理旧构建...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec.bak" del *.spec.bak
echo 完成！
echo.

echo [2/3] 开始打包（这可能需要几分钟）...
echo.

"C:\Program Files\Python311\Scripts\pyinstaller.exe" build.spec --clean

if %errorlevel% equ 0 (
    echo.
    echo [3/3] 打包完成！
    echo.
    echo ========================================
    echo 打包成功！
    echo.
    echo 可执行文件位置：
    echo dist\FastSunTools\FastSunTools.exe
    echo.
    echo 完整发布包位置：
    echo dist\FastSunTools\
    echo ========================================
    echo.
    echo 是否打开输出目录？ (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" explorer dist\FastSunTools
) else (
    echo.
    echo 打包失败！请检查错误信息。
    pause
)
