#!/usr/bin/env python3
"""
Python转EXE转换器 - 命令行工具入口
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from py2exe_converter.cli import main

if __name__ == '__main__':
    main()