"""
安静养鱼 - 打包脚本
使用方法: 
  1. 安装依赖: pip install pyinstaller pygame pyaudio
  2. 运行打包: pyinstaller quietfish.spec
  或
  python build.py
"""

import os
import sys
import subprocess

def install_deps():
    """安装打包依赖"""
    print("正在安装依赖...")
    packages = ["pyinstaller", "pygame", "PyAudio"]
    for pkg in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
    print("依赖安装完成！")

def build():
    """打包成exe"""
    print("正在打包，请稍候...")
    
    cmd = ["pyinstaller", "quietfish.spec", "--clean"]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ 打包完成！")
        print("📁 exe 文件位置: dist/QuietFish.exe")
    else:
        print("\n❌ 打包失败")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_deps()
    else:
        build()
