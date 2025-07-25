# Python转EXE自动化构建完整操作手册

## 📋 目录
1. [前置准备](#前置准备)
2. [项目文件检查](#项目文件检查)
3. [GitHub仓库设置](#github仓库设置)
4. [自动化构建配置](#自动化构建配置)
5. [触发构建](#触发构建)
6. [下载构建产物](#下载构建产物)
7. [故障排除](#故障排除)

---

## 🛠️ 前置准备

### 必需条件
- [ ] GitHub账号
- [ ] Git已安装并配置
- [ ] 本地项目代码准备完毕

### 验证Git配置
```bash
# 检查Git配置
git config --global user.name
git config --global user.email

# 如果未配置，请设置
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱@example.com"
```

---

## 📁 项目文件检查

### 当前项目必需文件清单
请确认以下文件存在且内容正确：

#### ✅ 核心文件
- [ ] `test_example.py` - 主程序文件
- [ ] `requirements.txt` - Python依赖
- [ ] `test_app.spec` - PyInstaller配置文件
- [ ] `api_test_app.spec` - API应用配置文件

#### ✅ 自动化配置文件
- [ ] `.github/workflows/build-windows.yml` - 基础构建流程
- [ ] `.github/workflows/cross-platform-build.yml` - 跨平台构建流程

### 文件内容验证
```bash
# 检查当前目录文件
ls -la

# 验证关键文件存在
ls .github/workflows/
ls *.spec
cat requirements.txt
```

---

## 🌐 GitHub仓库设置

### 步骤1: 创建GitHub仓库
1. 登录 [GitHub.com](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 填写仓库信息：
   - **Repository name**: `py2exe-builder` (或你喜欢的名称)
   - **Description**: `Python to EXE cross-platform builder`
   - 选择 **Public** (免费使用Actions)
   - 不要勾选任何初始化选项
4. 点击 **Create repository**

### 步骤2: 获取仓库地址
创建完成后，GitHub会显示类似这样的地址：
```
https://github.com/你的用户名/py2exe-builder.git
```
**📝 记录这个地址，后面会用到！**

---

## 🚀 自动化构建配置

### 步骤1: 初始化本地Git仓库
```bash
# 在项目目录下执行
cd /root/py2exe

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 创建首次提交
git commit -m "Initial commit with cross-platform build setup"
```

### 步骤2: 连接到GitHub仓库
```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/py2exe-builder.git

# 设置默认分支
git branch -M main
```

### 步骤3: 推送代码到GitHub
```bash
# 推送到GitHub
git push -u origin main
```

**🔒 如果提示需要认证：**
- 使用GitHub用户名
- 密码使用Personal Access Token (不是GitHub密码)
- 如需创建Token: GitHub → Settings → Developer settings → Personal access tokens

---

## ⚡ 触发构建

### 方法1: 自动触发（推荐新手）
每次推送代码都会自动构建：
```bash
# 修改代码后
git add .
git commit -m "Update application"
git push origin main
```

### 方法2: 创建发布版本（推荐正式发布）
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# 后续版本
git tag v1.0.1
git push origin v1.0.1
```

### 方法3: 手动触发
1. 前往GitHub仓库页面
2. 点击 **Actions** 选项卡
3. 选择工作流程
4. 点击 **Run workflow** 按钮

---

## 📦 下载构建产物

### 查看构建状态
1. 前往GitHub仓库 → **Actions**
2. 查看最新的构建任务
3. 等待构建完成（绿色✅表示成功）

### 下载开发版本
1. 点击完成的构建任务
2. 滚动到页面底部 **Artifacts** 部分
3. 下载对应平台的文件：
   - `windows-exe-xxx` - Windows可执行文件
   - `linux-binary-xxx` - Linux可执行文件

### 下载正式版本
1. 前往GitHub仓库 → **Releases**
2. 选择对应版本
3. 下载 **Assets** 中的文件

---

## 🔧 故障排除

### 问题1: Git推送失败
**现象**: `Permission denied` 或认证失败
**解决方案**:
1. 检查GitHub用户名和邮箱配置
2. 使用Personal Access Token作为密码
3. 或者使用SSH密钥认证

### 问题2: 构建失败
**现象**: Actions显示红色❌
**解决方案**:
1. 点击失败的构建查看日志
2. 检查 `requirements.txt` 中的依赖是否正确
3. 验证 `.spec` 文件配置

### 问题3: EXE文件无法运行
**现象**: Windows提示"无法运行"
**解决方案**:
1. 检查目标系统架构匹配
2. 安装Microsoft Visual C++ Redistributable
3. 在构建日志中查看具体错误

### 问题4: 依赖缺失
**现象**: 程序运行时报模块找不到
**解决方案**:
1. 在 `.spec` 文件中添加 `hiddenimports`
2. 更新 `requirements.txt` 包含所有依赖

---

## 📋 操作检查清单

### 首次设置
- [ ] GitHub仓库已创建
- [ ] 本地Git已配置
- [ ] 项目文件已检查
- [ ] 代码已推送到GitHub
- [ ] Actions工作流程已触发

### 每次发布
- [ ] 代码已测试
- [ ] 版本号已更新
- [ ] Git标签已创建
- [ ] 构建已完成
- [ ] EXE文件已下载并测试

---

## 🎯 下一步操作

1. **立即执行**: 按照本手册完成首次设置
2. **验证构建**: 等待第一次自动构建完成
3. **测试EXE**: 下载并在目标系统测试可执行文件
4. **发布版本**: 创建正式版本标签

---

## 📞 获取帮助

如果遇到问题：
1. 检查GitHub Actions构建日志
2. 查看本手册的故障排除部分
3. 确认所有必需文件都已正确创建

**🚀 祝你构建成功！**