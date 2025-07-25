#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试自动依赖安装功能的示例脚本
"""

import os
import sys
import requests
import websocket
from callpowershell import PowerShell

def main():
    print("测试依赖安装功能")
    print("此脚本包含多个第三方依赖包")
    
    # 测试requests
    try:
        response = requests.get("https://httpbin.org/json")
        print(f"requests测试成功: {response.status_code}")
    except Exception as e:
        print(f"requests测试失败: {e}")
    
    # 测试websocket
    try:
        ws = websocket.WebSocket()
        print("websocket模块导入成功")
    except Exception as e:
        print(f"websocket测试失败: {e}")
    
    # 测试callpowershell
    try:
        ps = PowerShell('UTF-8')
        print("callpowershell模块导入成功")
    except Exception as e:
        print(f"callpowershell测试失败: {e}")

if __name__ == "__main__":
    main()