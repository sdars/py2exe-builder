#!/bin/bash
# 项目文件检查脚本

echo "========================================"
echo "   Python to EXE 项目文件检查"
echo "========================================"

# 检查必需的Python文件
echo -e "\n📄 检查Python源文件..."
if [ -f "test_example.py" ]; then
    echo "✅ test_example.py - 存在"
else
    echo "❌ test_example.py - 缺失"
fi

if [ -f "example.py" ]; then
    echo "✅ example.py - 存在"
else
    echo "❌ example.py - 缺失"
fi

# 检查配置文件
echo -e "\n⚙️  检查配置文件..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt - 存在"
    echo "   依赖内容:"
    cat requirements.txt | sed 's/^/     /'
else
    echo "❌ requirements.txt - 缺失"
fi

if [ -f "test_app.spec" ]; then
    echo "✅ test_app.spec - 存在"
else
    echo "❌ test_app.spec - 缺失"
fi

if [ -f "api_test_app.spec" ]; then
    echo "✅ api_test_app.spec - 存在"
else
    echo "❌ api_test_app.spec - 缺失"
fi

# 检查GitHub Actions文件
echo -e "\n🔄 检查GitHub Actions配置..."
if [ -d ".github/workflows" ]; then
    echo "✅ .github/workflows/ - 目录存在"
    
    if [ -f ".github/workflows/build-windows.yml" ]; then
        echo "✅ build-windows.yml - 存在"
    else
        echo "❌ build-windows.yml - 缺失"
    fi
    
    if [ -f ".github/workflows/cross-platform-build.yml" ]; then
        echo "✅ cross-platform-build.yml - 存在"
    else
        echo "❌ cross-platform-build.yml - 缺失"
    fi
else
    echo "❌ .github/workflows/ - 目录缺失"
fi

# 检查Git状态
echo -e "\n📂 检查Git状态..."
if [ -d ".git" ]; then
    echo "✅ Git仓库已初始化"
    echo "   当前分支: $(git branch --show-current 2>/dev/null || echo '未设置')"
    echo "   远程仓库: $(git remote get-url origin 2>/dev/null || echo '未设置')"
else
    echo "❌ Git仓库未初始化"
fi

# 统计文件大小
echo -e "\n📊 项目统计..."
echo "   总文件数: $(find . -type f | wc -l)"
echo "   Python文件: $(find . -name "*.py" | wc -l)"
echo "   配置文件: $(find . -name "*.spec" -o -name "*.txt" -o -name "*.yml" | wc -l)"

echo -e "\n========================================"
echo "   检查完成！请参考上述结果确认项目状态"
echo "========================================"