"""构建脚本 - FastSunTools 打包工具

此脚本用于打包 FastSunTools 应用为可执行文件。
"""
import os
import sys
import subprocess


def build_application():
    """构建 FastSunTools 应用"""
    
    print()
    print("=" * 70)
    print("开始打包 FastSunTools...")
    print("=" * 70)
    print()
    
    # 导入 PyInstaller
    try:
        import PyInstaller.__main__
    except ImportError:
        print("需要安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # 运行 PyInstaller
    pyinstaller_path = r"C:\Program Files\Python311\Scripts\pyinstaller.exe"
    
    cmd = [
        pyinstaller_path,
        'build.spec',
        '--clean'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print()
        print("=" * 70)
        print("打包完成！")
        print("=" * 70)
        print()
        print("输出目录: dist/FastSunTools/")
        print()
        print("包含的内容:")
        print("  - FastSunTools.exe (主程序)")
        print("  - 所有依赖库")
        print()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e.stderr}")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    if build_application():
        print()
        print("打包成功！")
        sys.exit(0)
    else:
        sys.exit(1)
