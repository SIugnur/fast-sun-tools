import os
import shutil
import subprocess
import sys

def clean_build_dirs():
    """清理旧的构建目录"""
    dirs_to_clean = ['dist', 'build']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"正在删除 {dir_name}...")
            shutil.rmtree(dir_name)
    print("清理完成！")

def build_app():
    """使用 PyInstaller 打包应用"""
    print("\n开始打包...")
    
    # PyInstaller 路径
    pyinstaller_path = r"C:\Program Files\Python311\Scripts\pyinstaller.exe"
    
    # 构建命令
    cmd = [
        pyinstaller_path,
        'build.spec',
        '--clean'
    ]
    
    try:
        # 运行打包
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n" + "="*50)
        print("打包成功！")
        print("="*50)
        print(f"\n可执行文件位置：")
        print(f"  dist\\FastSunTools\\FastSunTools.exe")
        print(f"\n完整发布包位置：")
        print(f"  dist\\FastSunTools\\")
        print("\n" + "="*50)
        
        # 打开输出目录
        dist_path = os.path.join(os.getcwd(), 'dist', 'FastSunTools')
        if os.path.exists(dist_path):
            print(f"\n是否打开输出目录？")
            response = input("按回车键打开，或输入 N 跳过：")
            if response.strip().upper() != 'N':
                os.startfile(dist_path)
                
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败！错误信息：")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_build_dirs()
    build_app()
