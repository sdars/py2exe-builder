# Python转EXE转换器 使用手册

## 项目简介

Python转EXE转换器是一个功能完整的工具，可以将Python脚本转换为独立的可执行文件（.exe）。项目提供三种使用方式：

1. **命令行工具** - 适合自动化和批处理
2. **API服务** - 适合集成到其他系统
3. **网页控制台** - 适合直观的图形化操作

## 功能特性

- ✅ 支持单文件打包（--onefile）
- ✅ 支持无控制台窗口（--noconsole）
- ✅ 支持自定义图标
- ✅ 支持隐藏导入模块
- ✅ 支持添加额外数据文件
- ✅ Python文件语法验证
- ✅ 依赖模块自动检测
- ✅ Linux系统无桌面环境支持
- ✅ 实时转换进度显示
- ✅ 详细的错误信息提示

## 系统要求

- Python 3.8+
- PyInstaller 6.3.0+
- Flask 3.0.0+ (API服务模式)
- Linux/Windows/macOS

## 安装配置

### 1. 克隆项目
```bash
git clone <repository-url>
cd py2exe
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\\Scripts\\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：命令行工具

#### 基本用法
```bash
python py2exe.py script.py
```

#### 高级选项
```bash
# 无控制台窗口
python py2exe.py script.py --noconsole

# 指定图标
python py2exe.py script.py --icon app.ico

# 自定义名称
python py2exe.py script.py --name myapp

# 生成目录而非单文件
python py2exe.py script.py --onedir

# 指定输出目录
python py2exe.py script.py --output ./release

# 添加隐藏导入
python py2exe.py script.py --hidden-import requests

# 添加数据文件
python py2exe.py script.py --add-data "data.txt:."

# 详细输出
python py2exe.py script.py --verbose

# 仅验证文件
python py2exe.py script.py --validate-only
```

#### 完整示例
```bash
python py2exe.py example.py \\
    --noconsole \\
    --icon app.ico \\
    --name "MyApplication" \\
    --output ./release \\
    --hidden-import websocket \\
    --verbose
```

### 方式二：API服务

#### 启动服务
```bash
python server.py --host 0.0.0.0 --port 5000
```

#### API端点

**健康检查**
```bash
GET /api/health
```

**文件验证**
```bash
POST /api/validate
Content-Type: multipart/form-data

file: Python文件
```

**文件转换**
```bash
POST /api/convert
Content-Type: multipart/form-data

file: Python文件
icon: 图标文件（可选）
name: exe名称（可选）
noconsole: true/false
onefile: true/false
```

#### cURL示例
```bash
# 健康检查
curl -X GET http://localhost:5000/api/health

# 文件验证
curl -X POST -F "file=@script.py" http://localhost:5000/api/validate

# 文件转换
curl -X POST \\
  -F "file=@script.py" \\
  -F "icon=@app.ico" \\
  -F "name=myapp" \\
  -F "noconsole=true" \\
  http://localhost:5000/api/convert
```

### 方式三：网页控制台

1. 启动API服务：
```bash
python server.py
```

2. 打开浏览器访问：`http://localhost:5000`

3. 网页界面功能：
   - 📁 拖拽上传Python文件
   - 🔍 实时文件验证
   - 🎨 图标文件上传
   - ⚙️ 转换选项配置
   - 📊 依赖模块显示
   - 🚀 一键转换操作
   - 📋 详细结果展示

## 转换选项详解

### 核心选项

| 选项 | 说明 | 默认值 |
|-----|------|--------|
| `--noconsole` | 生成无控制台窗口的exe | False |
| `--onefile` | 打包为单个exe文件 | True |
| `--onedir` | 生成目录形式 | False |
| `--icon` | 指定exe图标文件 | None |
| `--name` | 自定义exe名称 | 脚本名 |

### 路径选项

| 选项 | 说明 | 默认值 |
|-----|------|--------|
| `--output` | 输出目录 | ./dist |
| `--workdir` | 工作目录 | ./build |

### 高级选项

| 选项 | 说明 | 用途 |
|-----|------|------|
| `--hidden-import` | 隐藏导入模块 | 解决导入问题 |
| `--add-data` | 添加数据文件 | 包含资源文件 |
| `--no-clean` | 不清理临时文件 | 调试用途 |

## 实际案例演示

### 案例1：转换示例脚本

**文件：** `test_example.py`
```python
#!/usr/bin/env python3
import os, sys, time, json
from datetime import datetime

class SimpleApp:
    def run(self):
        print("🚀 应用程序运行中...")
        # 应用逻辑
        
if __name__ == '__main__':
    app = SimpleApp()
    app.run()
```

**转换命令：**
```bash
python py2exe.py test_example.py --noconsole --name simple_app
```

**结果：**
- 生成文件：`./dist/simple_app`
- 文件大小：约7MB
- 运行方式：双击执行，无控制台窗口

### 案例2：转换复杂脚本

**文件：** `example.py`（包含websocket、ctypes等依赖）

**转换命令：**
```bash
python py2exe.py example.py \\
    --noconsole \\
    --name ecloud_img_report \\
    --hidden-import websocket \\
    --hidden-import ctypes \\
    --output ./production
```

**结果：**
- 生成文件：`./production/ecloud_img_report`
- 自动处理复杂依赖
- 适合生产环境部署

## 故障排除

### 常见问题

**1. 导入模块错误**
```
错误：ModuleNotFoundError: No module named 'xxx'
解决：使用 --hidden-import xxx 参数
```

**2. 缺少数据文件**
```
错误：FileNotFoundError: [Errno 2] No such file or directory
解决：使用 --add-data "source:dest" 参数
```

**3. 转换超时**
```
错误：Conversion timeout after 5 minutes
解决：检查文件大小和依赖复杂度
```

**4. 权限问题**
```
错误：Permission denied
解决：检查输出目录写入权限
```

### 调试技巧

**启用详细输出：**
```bash
python py2exe.py script.py --verbose
```

**保留临时文件：**
```bash
python py2exe.py script.py --no-clean
```

**仅验证不转换：**
```bash
python py2exe.py script.py --validate-only
```

## Linux无桌面环境部署

### 系统配置
```bash
# 安装必要包
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 创建项目目录
mkdir /opt/py2exe
cd /opt/py2exe
```

### 服务化部署
```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/py2exe.service << EOF
[Unit]
Description=Python to EXE Converter API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/py2exe
Environment=PATH=/opt/py2exe/venv/bin
ExecStart=/opt/py2exe/venv/bin/python server.py --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable py2exe
sudo systemctl start py2exe
```

### 防火墙配置
```bash
# 开放端口
sudo ufw allow 5000/tcp
```

## 性能优化

### 转换速度优化
- 使用SSD存储
- 增加内存分配
- 减少不必要的依赖
- 使用虚拟环境隔离

### 文件大小优化
```bash
# 排除不必要模块
python py2exe.py script.py --exclude-module tkinter

# 使用目录模式
python py2exe.py script.py --onedir
```

## 高级功能

### 批量转换脚本
```bash
#!/bin/bash
# batch_convert.sh

files=("app1.py" "app2.py" "app3.py")

for file in "${files[@]}"; do
    echo "转换 $file..."
    python py2exe.py "$file" --noconsole --output "./batch_dist"
done
```

### 自动化集成
```yaml
# GitHub Actions 示例
name: Build EXE
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Build EXE
      run: python py2exe.py app.py --noconsole
```

## API集成示例

### Python客户端
```python
import requests

# 上传转换
with open('script.py', 'rb') as f:
    files = {'file': f}
    data = {'noconsole': 'true', 'name': 'myapp'}
    response = requests.post('http://localhost:5000/api/convert', 
                           files=files, data=data)
    result = response.json()
    print(f"转换结果: {result}")
```

### JavaScript客户端
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('noconsole', 'true');

fetch('/api/convert', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log('转换结果:', data));
```

## 项目结构

```
py2exe/
├── py2exe_converter/          # 核心模块
│   ├── __init__.py
│   ├── core.py               # 转换核心逻辑
│   ├── api.py                # API服务
│   └── cli.py                # 命令行工具
├── py2exe.py                 # 命令行入口
├── server.py                 # API服务入口
├── requirements.txt          # 依赖列表
├── example.py               # 示例脚本
├── test_example.py          # 测试脚本
└── README.md               # 项目说明
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 支持与反馈

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 贡献代码

---

**最后更新：** 2024年7月25日  
**版本：** 1.0.0