#!/usr/bin/env python3
"""
Python转EXE转换器 - API服务器启动脚本
"""

import argparse
from py2exe_converter.api import PyToExeAPI


def main():
    parser = argparse.ArgumentParser(description='启动Python转EXE API服务')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print(f"🚀 启动Python转EXE API服务...")
    print(f"   地址: http://{args.host}:{args.port}")
    print(f"   网页控制台: http://{args.host}:{args.port}")
    print(f"   调试模式: {'开启' if args.debug else '关闭'}")
    print()
    
    api = PyToExeAPI()
    api.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()