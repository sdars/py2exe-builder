# 自动化构建说明

## GitHub Actions 工作流程

已创建两个自动化构建工作流程：

### 1. 基础构建 (build-windows.yml)
- **触发条件**: 推送到main/master分支、PR、手动触发
- **功能**: 同时构建Windows EXE和Linux二进制文件
- **输出**: 构建产物上传到Actions artifacts

### 2. 跨平台发布 (cross-platform-build.yml)
- **触发条件**: 创建版本标签 (v*.*)、手动触发
- **功能**: 构建Windows、Linux、macOS三个平台的可执行文件
- **输出**: 自动创建GitHub Release并上传文件

## 使用方法

### 设置仓库
1. 将代码推送到GitHub仓库
2. 确保仓库包含以下文件：
   - `requirements.txt`
   - `test_app.spec`
   - `api_test_app.spec`
   - `test_example.py`

### 触发构建

#### 方法1: 自动触发
```bash
git add .
git commit -m "Add cross-platform build"
git push origin main
```

#### 方法2: 创建发布版本
```bash
git tag v1.0.0
git push origin v1.0.0
```

#### 方法3: 手动触发
- 前往 GitHub 仓库的 Actions 页面
- 选择工作流程
- 点击 "Run workflow"

## 获取构建产物

### 开发版本
- 前往 Actions 页面
- 选择最新的构建
- 下载 Artifacts 中的文件

### 正式版本
- 前往 Releases 页面
- 下载对应版本的文件

## 优势

1. **自动化**: 无需手动配置Windows环境
2. **多平台**: 同时支持Windows、Linux、macOS
3. **可靠性**: 在真实的Windows环境中构建
4. **版本管理**: 自动创建发布版本
5. **免费**: GitHub Actions提供免费的构建时间

## 注意事项

- GitHub Actions每月提供2000分钟免费时间
- 私有仓库的构建时间计入配额
- 公开仓库的构建时间不计入配额