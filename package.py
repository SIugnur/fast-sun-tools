import paddlex
import importlib.metadata
import argparse
import subprocess
import sys
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True, help='Your file name, e.g. main.py.')
parser.add_argument('--nvidia', action='store_true', help='Include NVIDIA CUDA and cuDNN dependencies.')

args = parser.parse_args()

main_file = args.file

user_deps = [dist.metadata["Name"] for dist in importlib.metadata.distributions()]
deps_all = list(paddlex.utils.deps.BASE_DEP_SPECS.keys())
deps_need = [dep for dep in user_deps if dep in deps_all]

cmd = [
    "pyinstaller", main_file,
    "--collect-data", "paddlex",
    "--collect-data", "paddleocr",
    "--collect-data", "ppocr",
    "--collect-binaries", "paddle",
    "--hidden-import", "paddleocr",
    "--hidden-import", "ppocr",
]

if args.nvidia:
    cmd += ["--collect-binaries", "nvidia"]

for dep in deps_need:
    cmd += ["--copy-metadata", dep]

print("PyInstaller command:", " ".join(cmd))

try:
    result = subprocess.run(cmd, check=True)
    print("PyInstaller completed successfully!")
    
    # 复制PaddleOCR配置和模型文件到dist目录
    dist_dir = os.path.join("dist", "FastSunTools", "_internal")
    
    # 复制PPOCR资源文件
    ppocr_src = Path(sys.prefix) / "Lib" / "site-packages" / "ppocr"
    ppocr_dst = os.path.join(dist_dir, "ppocr")
    
    if ppocr_src.exists():
        print(f"Copying PPOCR resources from {ppocr_src}")
        os.makedirs(ppocr_dst, exist_ok=True)
        
        # 复制所有文件和子目录
        for item in ppocr_src.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(ppocr_src)
                dst_path = os.path.join(ppocr_dst, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                try:
                    import shutil
                    shutil.copy2(item, dst_path)
                except Exception as e:
                    print(f"Warning: Failed to copy {item}: {e}")
        
        print("PPOCR resources copied successfully!")
    else:
        print("Warning: PPOCR directory not found")
        
except subprocess.CalledProcessError as e:
    print("Installation failed:", e)
    sys.exit(1)
