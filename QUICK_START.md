# 🚀 Python转EXE自动化构建 - 快速启动指南

## 📋 概述
这是一个完整的、一键式的Python转Windows EXE自动化构建解决方案。通过GitHub Actions，您可以在Linux环境下开发，自动生成Windows、Linux、macOS三个平台的可执行文件。

## ⚡ 快速开始（3分钟完成设置）

### 方法1: 一键脚本（推荐）
```bash
chmod +x setup_github_actions.sh
./setup_github_actions.sh
```

### 方法2: 手动步骤
如果您喜欢手动控制每个步骤：

#### 1. 检查项目状态
```bash
./check_project.sh
```

#### 2. 初始化Git
```bash
git init
git add .
git commit -m "Initial commit"
```

#### 3. 创建GitHub仓库
- 访问 https://github.com/new
- 仓库名：`py2exe-builder`
- 设为Public
- 不勾选初始化选项

#### 4. 连接仓库并推送
```bash
git remote add origin https://github.com/你的用户名/py2exe-builder.git
git branch -M main
git push -u origin main
```

## 📁 项目文件结构

```
py2exe/
├── 📄 源代码文件
│   ├── test_example.py          # 主程序
│   └── example.py               # 原始示例
├── ⚙️ 配置文件  
│   ├── requirements.txt         # Python依赖
│   ├── test_app.spec           # PyInstaller配置
│   └── api_test_app.spec       # API应用配置
├── 🔄 自动化配置
│   └── .github/workflows/
│       ├── build-windows.yml       # 基础构建流程
│       └── cross-platform-build.yml # 跨平台发布流程
├── 📖 文档
│   ├── COMPLETE_SETUP_GUIDE.md     # 完整操作手册
│   ├── GITHUB_ACTIONS_GUIDE.md     # GitHub Actions指南
│   └── QUICK_START.md              # 本文件
└── 🛠️ 工具脚本
    ├── check_project.sh            # 项目检查
    └── setup_github_actions.sh     # 一键设置
```

## 🎯 构建触发方式

### 自动触发
- 推送到main分支自动构建开发版本
- 创建标签自动构建发布版本

### 手动触发
- GitHub仓库 → Actions → Run workflow

### 发布版本
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 📦 获取构建产物

### 开发版本
1. GitHub仓库 → Actions
2. 选择最新构建
3. 下载Artifacts中的文件

### 正式版本  
1. GitHub仓库 → Releases
2. 下载对应版本文件

## 🔍 支持的平台

| 平台 | 输出文件 | 说明 |
|------|----------|------|
| Windows | `.exe` | 64位可执行文件 |
| Linux | 二进制文件 | 64位可执行文件 |
| macOS | 二进制文件 | 64位可执行文件 |

## ⚠️ 常见问题

### Q: 推送失败，提示认证错误？
A: 使用Personal Access Token作为密码，不是GitHub登录密码
- 创建Token: GitHub → Settings → Developer settings → Personal access tokens

### Q: 构建失败怎么办？
A: 查看GitHub Actions的构建日志，通常是依赖或配置问题

### Q: EXE文件无法运行？
A: 检查目标系统是否安装了Microsoft Visual C++ Redistributable

## 🛠️ 自定义配置

### 修改应用程序
编辑 `test_example.py` 文件，然后推送代码即可自动构建

### 添加依赖
在 `requirements.txt` 中添加新的Python包

### 修改构建配置
编辑 `.spec` 文件调整PyInstaller设置

## 📈 优势特点

- ✅ **零配置**: 一键脚本完成所有设置
- ✅ **跨平台**: 同时支持Windows/Linux/macOS
- ✅ **自动化**: 推送代码自动构建
- ✅ **免费**: GitHub Actions免费使用
- ✅ **可靠**: 在真实系统环境中构建
- ✅ **版本管理**: 自动创建发布版本

## 🎉 立即开始

1. 执行一键脚本：`./setup_github_actions.sh`
2. 等待构建完成
3. 下载您的EXE文件
4. 在目标系统测试运行

**🚀 从Python代码到跨平台可执行文件，只需3分钟！**