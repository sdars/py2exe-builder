# 🔧 故障排除与常见问题解决指南

## 📋 目录
1. [Git相关问题](#git相关问题)
2. [GitHub Actions构建问题](#github-actions构建问题)
3. [EXE运行问题](#exe运行问题)
4. [依赖和配置问题](#依赖和配置问题)
5. [认证和权限问题](#认证和权限问题)

---

## 🔀 Git相关问题

### ❌ 问题1: `git: command not found`
**现象**: 执行git命令时提示找不到命令
**解决方案**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# CentOS/RHEL
sudo yum install git

# 验证安装
git --version
```

### ❌ 问题2: 推送失败 - `Permission denied`
**现象**: `git push` 时提示权限拒绝
**解决方案**:
1. **使用Personal Access Token**:
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择权限：repo, workflow
   - 复制生成的token
   - 推送时用token作为密码

2. **或使用SSH密钥**:
```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到GitHub
cat ~/.ssh/id_ed25519.pub
# 复制内容到 GitHub → Settings → SSH keys

# 更改仓库URL为SSH
git remote set-url origin git@github.com:username/repo.git
```

### ❌ 问题3: `fatal: not a git repository`
**现象**: 执行git命令时提示不是git仓库
**解决方案**:
```bash
# 确认在正确目录
pwd
ls -la .git

# 如果没有.git目录，初始化仓库
git init
```

---

## 🔄 GitHub Actions构建问题

### ❌ 问题4: 构建失败 - 依赖安装错误
**现象**: Actions日志显示pip安装失败
**解决方案**:
1. **检查requirements.txt格式**:
```txt
# 正确格式
pyinstaller==6.3.0
flask==3.0.0

# 错误格式（有多余空格或字符）
pyinstaller == 6.3.0
flask >= 3.0.0
```

2. **更新requirements.txt**:
```bash
# 重新生成依赖文件
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### ❌ 问题5: PyInstaller构建失败
**现象**: 构建过程中PyInstaller报错
**解决方案**:
1. **检查spec文件语法**:
```python
# 确保没有语法错误
python -c "exec(open('test_app.spec').read())"
```

2. **添加缺失的隐藏导入**:
```python
# 在spec文件中添加
hiddenimports=['your_missing_module'],
```

### ❌ 问题6: 构建超时
**现象**: Actions构建超过时间限制
**解决方案**:
1. **优化spec文件**:
```python
# 禁用UPX压缩加速构建
upx=False,
```

2. **分离构建步骤**:
```yaml
# 在workflow中增加超时设置
timeout-minutes: 30
```

---

## 💻 EXE运行问题

### ❌ 问题7: "此应用无法在你的电脑上运行"
**现象**: Windows系统提示应用无法运行
**解决方案**:
1. **检查架构匹配**:
   - 确保spec文件中 `target_arch='x86_64'`
   - 在64位Windows系统运行64位程序

2. **安装Visual C++ Redistributable**:
   - 下载并安装最新版本
   - 链接: https://aka.ms/vs/17/release/vc_redist.x64.exe

3. **检查Windows版本兼容性**:
   - Windows 10/11 建议使用
   - Windows 7需要额外补丁

### ❌ 问题8: EXE启动后立即退出
**现象**: 双击EXE后闪退，没有错误信息
**解决方案**:
1. **在命令行运行查看错误**:
```cmd
# 在Windows命令行中运行
.\test_app.exe
```

2. **启用控制台输出**:
```python
# 在spec文件中设置
console=True,
```

3. **添加异常处理**:
```python
# 在Python代码中添加
try:
    main()
except Exception as e:
    print(f"错误: {e}")
    input("按回车键退出...")
```

### ❌ 问题9: 缺少DLL文件
**现象**: 提示缺少某个.dll文件
**解决方案**:
1. **手动添加DLL**:
```python
# 在spec文件中添加
binaries=[('path/to/your.dll', '.')],
```

2. **安装系统依赖**:
```bash
# 在Windows上安装相关运行库
# Microsoft Visual C++ Redistributable
# .NET Framework (如果需要)
```

---

## 📦 依赖和配置问题

### ❌ 问题10: 模块导入错误
**现象**: EXE运行时提示"No module named 'xxx'"
**解决方案**:
1. **添加隐藏导入**:
```python
# 在spec文件中添加
hiddenimports=['missing_module', 'another_module'],
```

2. **检查虚拟环境**:
```bash
# 确保在正确的虚拟环境中
source venv/bin/activate  # Linux
# 或
venv\Scripts\activate     # Windows
```

### ❌ 问题11: 资源文件缺失
**现象**: 程序找不到配置文件或数据文件
**解决方案**:
```python
# 在spec文件中添加数据文件
datas=[('config.json', '.'), ('data/', 'data/')],
```

---

## 🔐 认证和权限问题

### ❌ 问题12: GitHub Actions权限不足
**现象**: 无法创建Release或上传文件
**解决方案**:
1. **检查仓库设置**:
   - Settings → Actions → General
   - 确保 "Read and write permissions" 已启用

2. **检查token权限**:
```yaml
# 在workflow中添加权限
permissions:
  contents: write
  actions: read
```

### ❌ 问题13: 无法访问私有仓库
**现象**: Actions无法访问依赖的私有仓库
**解决方案**:
```yaml
# 在workflow中使用PAT
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

---

## 🛠️ 调试技巧

### 🔍 诊断脚本
创建诊断脚本快速定位问题：
```bash
#!/bin/bash
echo "=== 系统诊断 ==="
echo "Git版本: $(git --version)"
echo "Python版本: $(python --version)"
echo "当前目录: $(pwd)"
echo "Git状态: $(git status --porcelain | wc -l) 个修改"
echo "远程仓库: $(git remote -v)"

echo -e "\n=== 文件检查 ==="
ls -la *.py *.spec *.txt .github/workflows/

echo -e "\n=== 最近提交 ==="
git log --oneline -5
```

### 📝 日志分析
1. **GitHub Actions日志**:
   - 点击失败的构建
   - 展开每个步骤查看详细输出
   - 搜索关键词：ERROR, FAILED, Exception

2. **本地调试**:
```bash
# 本地测试PyInstaller
source venv/bin/activate
pyinstaller test_app.spec --clean --log-level DEBUG
```

### 🔄 常用修复命令
```bash
# 重置Git状态
git reset --hard HEAD
git clean -fd

# 强制推送（谨慎使用）
git push --force-with-lease origin main

# 重新构建
rm -rf build/ dist/
pyinstaller test_app.spec --clean
```

---

## 📞 获取更多帮助

### 📚 官方文档
- [PyInstaller文档](https://pyinstaller.readthedocs.io/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Git官方文档](https://git-scm.com/doc)

### 🆘 社区支持
- GitHub Issues: 在项目仓库创建issue
- Stack Overflow: 搜索相关错误信息
- PyInstaller用户群

### 💡 预防措施
1. **定期备份**: 使用Git标签标记稳定版本
2. **测试验证**: 在目标系统测试EXE文件
3. **版本管理**: 记录依赖版本避免冲突
4. **文档维护**: 更新配置时同步更新文档

---

**🎯 记住：大部分问题都有解决方案，保持耐心，仔细阅读错误信息！**