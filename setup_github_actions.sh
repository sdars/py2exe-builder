#!/bin/bash
# GitHub自动化构建快速启动脚本

echo "========================================"
echo "   GitHub自动化构建 - 一键设置"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 步骤1: 检查Git配置
echo -e "\n${BLUE}步骤1: 检查Git配置${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装，请先安装Git${NC}"
    exit 1
fi

# 检查用户名和邮箱
USER_NAME=$(git config --global user.name)
USER_EMAIL=$(git config --global user.email)

if [ -z "$USER_NAME" ] || [ -z "$USER_EMAIL" ]; then
    echo -e "${YELLOW}⚠️  Git用户信息未配置${NC}"
    echo -e "请输入您的GitHub用户名:"
    read -r github_username
    echo -e "请输入您的邮箱:"
    read -r github_email
    
    git config --global user.name "$github_username"
    git config --global user.email "$github_email"
    echo -e "${GREEN}✅ Git配置已更新${NC}"
else
    echo -e "${GREEN}✅ Git已配置: $USER_NAME <$USER_EMAIL>${NC}"
fi

# 步骤2: 初始化Git仓库
echo -e "\n${BLUE}步骤2: 初始化Git仓库${NC}"
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✅ Git仓库已初始化${NC}"
else
    echo -e "${GREEN}✅ Git仓库已存在${NC}"
fi

# 步骤3: 创建.gitignore
echo -e "\n${BLUE}步骤3: 创建.gitignore文件${NC}"
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec.bak

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
server.pid

# Temporary files
*.tmp
*.temp
python-*.exe
EOF
echo -e "${GREEN}✅ .gitignore文件已创建${NC}"

# 步骤4: 添加所有文件
echo -e "\n${BLUE}步骤4: 添加项目文件${NC}"
git add .
echo -e "${GREEN}✅ 所有文件已添加到Git${NC}"

# 步骤5: 创建初始提交
echo -e "\n${BLUE}步骤5: 创建初始提交${NC}"
git commit -m "Initial commit: Python to EXE cross-platform builder

- Add Python source files
- Add PyInstaller spec configurations
- Add GitHub Actions workflows for automated building
- Support Windows, Linux, and macOS builds"

echo -e "${GREEN}✅ 初始提交已创建${NC}"

# 步骤6: 设置GitHub仓库
echo -e "\n${BLUE}步骤6: 设置GitHub远程仓库${NC}"
echo -e "${YELLOW}请按照以下步骤操作:${NC}"
echo -e "1. 打开浏览器访问: ${BLUE}https://github.com/new${NC}"
echo -e "2. 仓库名称输入: ${GREEN}py2exe-builder${NC}"
echo -e "3. 选择 ${GREEN}Public${NC} (免费使用GitHub Actions)"
echo -e "4. ${RED}不要${NC}勾选任何初始化选项"
echo -e "5. 点击 ${GREEN}Create repository${NC}"
echo -e "\n创建完成后，请输入仓库URL (格式: https://github.com/用户名/仓库名.git):"
read -r repo_url

if [ -n "$repo_url" ]; then
    git remote add origin "$repo_url"
    git branch -M main
    echo -e "${GREEN}✅ 远程仓库已配置: $repo_url${NC}"
else
    echo -e "${YELLOW}⚠️  跳过远程仓库配置${NC}"
fi

# 步骤7: 推送到GitHub
echo -e "\n${BLUE}步骤7: 推送代码到GitHub${NC}"
if git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}准备推送代码到GitHub...${NC}"
    echo -e "${YELLOW}如果提示认证，请使用:${NC}"
    echo -e "  用户名: 您的GitHub用户名"
    echo -e "  密码: Personal Access Token (不是GitHub密码)"
    echo -e "\n按回车继续推送，或按Ctrl+C取消..."
    read -r
    
    # 尝试推送，如果失败则处理冲突
    if git push -u origin main; then
        echo -e "${GREEN}✅ 代码已成功推送到GitHub${NC}"
    else
        echo -e "${YELLOW}⚠️  推送失败，可能存在冲突${NC}"
        
        # 检查是否是因为远程有新提交导致的冲突
        git fetch origin main 2>/dev/null
        if git log HEAD..origin/main --oneline | grep -q .; then
            echo -e "${YELLOW}检测到远程仓库有新的提交，需要处理冲突${NC}"
            echo -e "\n${BLUE}请选择处理方式:${NC}"
            echo -e "1. ${GREEN}强制推送${NC} (用本地代码覆盖远程，推荐)"
            echo -e "2. ${YELLOW}先拉取再推送${NC} (合并远程更改)"
            echo -e "3. ${RED}取消推送${NC}"
            
            while true; do
                read -p "请输入选择 (1/2/3，默认为1): " choice
                choice=${choice:-1}
                
                case $choice in
                    1)
                        echo -e "${YELLOW}正在强制推送...${NC}"
                        if git push -u origin main --force; then
                            echo -e "${GREEN}✅ 强制推送成功${NC}"
                        else
                            echo -e "${RED}❌ 强制推送失败，请检查认证信息${NC}"
                            echo -e "${YELLOW}💡 提示: 如需创建Token，访问: https://github.com/settings/tokens${NC}"
                        fi
                        break
                        ;;
                    2)
                        echo -e "${YELLOW}正在拉取远程更改...${NC}"
                        if git pull origin main --no-rebase; then
                            echo -e "${GREEN}✅ 合并完成，正在推送...${NC}"
                            if git push -u origin main; then
                                echo -e "${GREEN}✅ 推送成功${NC}"
                            else
                                echo -e "${RED}❌ 推送失败，请检查认证信息${NC}"
                                echo -e "${YELLOW}💡 提示: 如需创建Token，访问: https://github.com/settings/tokens${NC}"
                            fi
                        else
                            echo -e "${RED}❌ 拉取失败，请手动处理冲突${NC}"
                        fi
                        break
                        ;;
                    3)
                        echo -e "${YELLOW}已取消推送${NC}"
                        break
                        ;;
                    *)
                        echo -e "${RED}无效选择，请输入 1、2 或 3${NC}"
                        ;;
                esac
            done
        else
            echo -e "${RED}❌ 推送失败，请检查认证信息${NC}"
            echo -e "${YELLOW}💡 提示: 如需创建Token，访问: https://github.com/settings/tokens${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  远程仓库未配置，跳过推送${NC}"
fi

# 完成提示
echo -e "\n========================================"
echo -e "${GREEN}   🎉 设置完成！${NC}"
echo -e "========================================"

if git remote get-url origin &> /dev/null; then
    REPO_URL=$(git remote get-url origin)
    REPO_NAME=$(basename "$REPO_URL" .git)
    USER_NAME=$(dirname "$REPO_URL" | basename)
    
    echo -e "\n${BLUE}📋 下一步操作:${NC}"
    echo -e "1. 访问仓库: ${GREEN}$REPO_URL${NC}"
    echo -e "2. 点击 ${GREEN}Actions${NC} 选项卡查看构建状态"
    echo -e "3. 等待构建完成后下载EXE文件"
    
    echo -e "\n${BLUE}🔗 快捷链接:${NC}"
    echo -e "- 仓库主页: ${GREEN}https://github.com/$USER_NAME/$REPO_NAME${NC}"
    echo -e "- Actions页面: ${GREEN}https://github.com/$USER_NAME/$REPO_NAME/actions${NC}"
    echo -e "- Releases页面: ${GREEN}https://github.com/$USER_NAME/$REPO_NAME/releases${NC}"
    
    echo -e "\n${BLUE}📦 创建发布版本:${NC}"
    echo -e "git tag v1.0.0"
    echo -e "git push origin v1.0.0"
else
    echo -e "\n${YELLOW}请手动配置GitHub仓库后继续${NC}"
fi

echo -e "\n${GREEN}🚀 祝您构建成功！${NC}"