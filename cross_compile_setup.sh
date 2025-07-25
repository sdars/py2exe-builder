#!/bin/bash
# Windows交叉编译环境设置脚本

echo "=== 设置Wine环境用于Python Windows打包 ==="

# 设置Wine前缀
export WINEPREFIX=$HOME/.wine-pyinstaller
export WINEARCH=win64

# 初始化Wine环境
echo "初始化Wine环境..."
winecfg &
sleep 5
pkill winecfg

# 下载Windows Python安装包
PYTHON_VERSION="3.11.8"
PYTHON_INSTALLER="python-${PYTHON_VERSION}-amd64.exe"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_INSTALLER}"

echo "下载Python Windows版本..."
if [ ! -f "$PYTHON_INSTALLER" ]; then
    wget "$PYTHON_URL"
fi

# 安装Python到Wine环境
echo "在Wine中安装Python..."
wine "$PYTHON_INSTALLER" /quiet InstallAllUsers=1 PrependPath=1

# 等待安装完成
sleep 30

# 验证安装
echo "验证Python安装..."
wine python --version

# 安装PyInstaller
echo "安装PyInstaller..."
wine python -m pip install pyinstaller

echo "设置完成！"
echo "使用方法："
echo "  export WINEPREFIX=$HOME/.wine-pyinstaller"
echo "  wine python -m PyInstaller your_script.py"