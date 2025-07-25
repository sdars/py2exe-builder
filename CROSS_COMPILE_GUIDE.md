# Linux下生成Windows EXE的解决方案

## 方案概述

PyInstaller本身不支持真正的交叉编译，但有以下几种方案可以在Linux上生成Windows exe：

## 方案1: 使用Wine (推荐)

### 优点
- 可以在Linux上直接运行
- 相对简单的设置过程
- 生成真正的Windows exe

### 设置步骤
1. 安装Windows Python到Wine环境
2. 在Wine中安装PyInstaller
3. 使用Wine运行PyInstaller

### 使用脚本
```bash
chmod +x cross_compile_setup.sh
./cross_compile_setup.sh
```

## 方案2: GitHub Actions自动化

创建 `.github/workflows/build-windows.yml`:

```yaml
name: Build Windows EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: pyinstaller test_app.spec
    - uses: actions/upload-artifact@v3
      with:
        name: windows-exe
        path: dist/
```

## 方案3: 远程Windows环境

- 使用云服务器Windows实例
- 通过SSH/RDP连接进行打包
- 设置CI/CD自动化流程

## 方案4: 虚拟机

- 在Linux上运行Windows虚拟机
- 在虚拟机中进行Python打包
- 通过共享文件夹传输结果

## 推荐流程

1. **开发环境**: Linux进行开发和测试
2. **打包环境**: 使用GitHub Actions或Wine进行Windows打包
3. **测试验证**: 在真实Windows环境中测试exe文件

## 注意事项

- Wine方案可能存在兼容性问题
- 最可靠的方法仍是在真实Windows环境打包
- GitHub Actions是最推荐的自动化方案