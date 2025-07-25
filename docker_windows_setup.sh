#!/bin/bash
# 使用Docker进行Windows交叉编译

echo "=== 使用Docker进行Windows Python打包 ==="

# 创建Dockerfile
cat > Dockerfile.windows << 'EOF'
# 使用Windows Server Core镜像
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# 设置工作目录
WORKDIR C:\\app

# 下载并安装Python
ADD https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe python-installer.exe
RUN python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

# 安装PyInstaller
RUN python -m pip install pyinstaller

# 复制源代码
COPY . .

# 构建EXE
CMD ["python", "-m", "PyInstaller", "--onefile", "test_example.py"]
EOF

echo "Dockerfile已创建，但需要Windows Docker环境"
echo "Linux Docker无法运行Windows容器"