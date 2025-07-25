#!/usr/bin/env python3
"""
Python转EXE命令行工具
支持通过命令行参数进行Python文件转换
"""

import argparse
import sys
import os
import json
from pathlib import Path
from .core import PyToExeConverter


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Python转EXE转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  %(prog)s script.py                           # 基本转换
  %(prog)s script.py --noconsole               # 无控制台窗口
  %(prog)s script.py --icon app.ico            # 指定图标
  %(prog)s script.py --name myapp              # 指定名称
  %(prog)s script.py --onedir                  # 生成目录而非单文件
  %(prog)s script.py --output ./dist           # 指定输出目录
        '''
    )
    
    # 必需参数
    parser.add_argument('python_file', help='要转换的Python文件路径')
    
    # 可选参数
    parser.add_argument('--noconsole', action='store_true',
                        help='生成无控制台窗口的exe文件')
    parser.add_argument('--onedir', action='store_true',
                        help='生成目录形式而非单个exe文件')
    parser.add_argument('--icon', type=str,
                        help='指定exe文件的图标(.ico文件)')
    parser.add_argument('--name', type=str,
                        help='指定生成的exe文件名称')
    parser.add_argument('--output', type=str, default='./dist',
                        help='指定输出目录 (默认: ./dist)')
    parser.add_argument('--workdir', type=str, default='./build',
                        help='指定工作目录 (默认: ./build)')
    parser.add_argument('--hidden-import', action='append', dest='hidden_imports',
                        help='指定隐藏导入的模块 (可多次使用)')
    parser.add_argument('--add-data', action='append', dest='additional_data',
                        help='添加额外数据文件 (格式: source:destination)')
    parser.add_argument('--no-clean', action='store_true',
                        help='不清理临时文件')
    parser.add_argument('--validate-only', action='store_true',
                        help='仅验证Python文件，不进行转换')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细输出')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='静默模式，只显示错误')
    parser.add_argument('--no-auto-deps', action='store_true',
                        help='不自动安装缺失的依赖包')
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = PyToExeConverter()
    
    # 验证Python文件
    if not os.path.exists(args.python_file):
        print(f"错误: Python文件不存在: {args.python_file}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"正在验证文件: {args.python_file}")
    
    validation = converter.validate_python_file(args.python_file)
    if not validation['valid']:
        print(f"错误: {validation['error']}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"文件验证成功，大小: {validation['size']} 字节")
        deps = converter.get_dependencies(args.python_file)
        if deps:
            print(f"检测到依赖: {', '.join(deps)}")
    
    # 如果只是验证，则退出
    if args.validate_only:
        print("✅ 文件验证通过")
        if not args.quiet:
            deps = converter.get_dependencies(args.python_file)
            if deps:
                print(f"依赖模块: {', '.join(deps)}")
        sys.exit(0)
    
    # 构建转换选项
    options = {
        'noconsole': args.noconsole,
        'onefile': not args.onedir,
        'distpath': args.output,
        'workpath': args.workdir,
        'clean': not args.no_clean,
        'auto_install_deps': not args.no_auto_deps
    }
    
    if args.icon:
        if not os.path.exists(args.icon):
            print(f"错误: 图标文件不存在: {args.icon}", file=sys.stderr)
            sys.exit(1)
        options['icon'] = args.icon
    
    if args.name:
        options['name'] = args.name
    
    if args.hidden_imports:
        options['hidden_imports'] = args.hidden_imports
    
    if args.additional_data:
        options['additional_data'] = args.additional_data
    
    # 执行转换
    if not args.quiet:
        print("🚀 开始转换...")
        if args.verbose:
            print(f"转换选项: {json.dumps(options, indent=2, ensure_ascii=False)}")
    
    result = converter.convert(args.python_file, options)
    
    if result['success']:
        if not args.quiet:
            print("🎉 转换成功!")
            print(f"EXE文件位置: {result['exe_path']}")
        
        if args.verbose and result.get('stdout'):
            print("\n详细输出:")
            print(result['stdout'])
        
        sys.exit(0)
    else:
        print(f"❌ 转换失败: {result['error']}", file=sys.stderr)
        
        if args.verbose:
            if result.get('stdout'):
                print("\n标准输出:", file=sys.stderr)
                print(result['stdout'], file=sys.stderr)
            if result.get('stderr'):
                print("\n错误输出:", file=sys.stderr)
                print(result['stderr'], file=sys.stderr)
        
        sys.exit(1)


if __name__ == '__main__':
    main()