import os
import sys
import json
import subprocess
import tempfile
import shutil
import pkg_resources
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional


class PyToExeConverter:
    """Python到exe文件转换器核心类"""
    
    def __init__(self):
        self.temp_dir = None
        self.default_options = {
            'onefile': True,
            'noconsole': True,
            'icon': None,
            'hidden_imports': [],
            'additional_data': [],
            'name': None,
            'distpath': './dist',
            'workpath': './build',
            'clean': True
        }
    
    def convert(self, python_file: str, options: Dict = None) -> Dict:
        """
        转换Python文件为exe
        
        Args:
            python_file: Python文件路径
            options: 转换选项
            
        Returns:
            转换结果字典
        """
        try:
            # 合并选项
            final_options = self.default_options.copy()
            if options:
                final_options.update(options)
            
            # 验证文件存在
            if not os.path.exists(python_file):
                return {
                    'success': False,
                    'error': f'Python file not found: {python_file}'
                }
            
            # 检查并自动安装依赖
            auto_install = final_options.get('auto_install_deps', True)
            if auto_install:
                deps_result = self.check_and_install_dependencies(python_file)
                if not deps_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to install dependencies: {deps_result["error"]}'
                    }
            
            # 生成PyInstaller命令
            cmd = self._build_pyinstaller_command(python_file, final_options)
            
            # 执行转换
            result = self._execute_conversion(cmd, final_options)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_pyinstaller_command(self, python_file: str, options: Dict) -> List[str]:
        """构建PyInstaller命令"""
        cmd = ['pyinstaller']
        
        # 基本选项
        if options.get('onefile'):
            cmd.append('--onefile')
        
        if options.get('noconsole'):
            cmd.append('--noconsole')
        
        # 图标
        if options.get('icon'):
            cmd.extend(['--icon', options['icon']])
        
        # 隐藏导入
        for imp in options.get('hidden_imports', []):
            cmd.extend(['--hidden-import', imp])
        
        # 额外数据
        for data in options.get('additional_data', []):
            cmd.extend(['--add-data', data])
        
        # 输出目录
        if options.get('distpath'):
            cmd.extend(['--distpath', options['distpath']])
        
        if options.get('workpath'):
            cmd.extend(['--workpath', options['workpath']])
        
        # 名称
        if options.get('name'):
            cmd.extend(['--name', options['name']])
        
        # 清理
        if options.get('clean'):
            cmd.append('--clean')
        
        # Python文件
        cmd.append(python_file)
        
        return cmd
    
    def _execute_conversion(self, cmd: List[str], options: Dict) -> Dict:
        """执行转换命令"""
        try:
            # 执行命令
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if process.returncode == 0:
                # 成功
                exe_path = self._find_exe_file(options)
                return {
                    'success': True,
                    'exe_path': exe_path,
                    'stdout': process.stdout,
                    'stderr': process.stderr
                }
            else:
                # 失败
                return {
                    'success': False,
                    'error': f'PyInstaller failed with return code {process.returncode}',
                    'stdout': process.stdout,
                    'stderr': process.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Conversion timeout after 5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_exe_file(self, options: Dict) -> Optional[str]:
        """查找生成的exe文件"""
        dist_path = options.get('distpath', './dist')
        
        if not os.path.exists(dist_path):
            return None
        
        # 查找exe文件
        for root, dirs, files in os.walk(dist_path):
            for file in files:
                if file.endswith('.exe'):
                    return os.path.join(root, file)
        
        return None
    
    def validate_python_file(self, file_path: str) -> Dict:
        """验证Python文件"""
        try:
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': 'File does not exist'
                }
            
            if not file_path.endswith('.py'):
                return {
                    'valid': False,
                    'error': 'File is not a Python file'
                }
            
            # 尝试编译检查语法
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            try:
                compile(source, file_path, 'exec')
            except SyntaxError as e:
                return {
                    'valid': False,
                    'error': f'Syntax error: {str(e)}'
                }
            
            return {
                'valid': True,
                'size': os.path.getsize(file_path)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_dependencies(self, python_file: str) -> List[str]:
        """获取Python文件依赖"""
        dependencies = []
        
        try:
            with open(python_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的import解析
            import ast
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
            
            return list(set(dependencies))
            
        except Exception:
            return []
    
    def check_and_install_dependencies(self, python_file: str) -> Dict:
        """检查并自动安装缺失依赖"""
        try:
            # 获取文件的依赖
            dependencies = self.get_dependencies(python_file)
            missing_deps = []
            
            # 检查哪些依赖缺失
            for dep in dependencies:
                if not self._is_module_installed(dep):
                    missing_deps.append(dep)
            
            if not missing_deps:
                return {'success': True, 'message': 'All dependencies are already installed'}
            
            # 尝试自动安装缺失的依赖
            installed_deps = []
            failed_deps = []
            
            for dep in missing_deps:
                if self._install_package(dep):
                    installed_deps.append(dep)
                else:
                    failed_deps.append(dep)
            
            if failed_deps:
                return {
                    'success': False,
                    'error': f'Failed to install: {", ".join(failed_deps)}',
                    'installed': installed_deps,
                    'failed': failed_deps
                }
            
            return {
                'success': True,
                'message': f'Successfully installed: {", ".join(installed_deps)}',
                'installed': installed_deps
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_module_installed(self, module_name: str) -> bool:
        """检查模块是否已安装"""
        # 处理子模块，只检查顶级模块
        top_level_module = module_name.split('.')[0]
        
        # 跳过标准库模块
        if self._is_standard_library(top_level_module):
            return True
        
        try:
            # 尝试导入模块
            spec = importlib.util.find_spec(top_level_module)
            return spec is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False
    
    def _is_standard_library(self, module_name: str) -> bool:
        """检查是否为标准库模块"""
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'random', 'hashlib',
            'logging', 'threading', 'subprocess', 'pathlib', 'tempfile',
            'shutil', 'collections', 'itertools', 'functools', 'operator',
            'math', 'statistics', 're', 'string', 'io', 'base64', 'binascii',
            'struct', 'codecs', 'unicodedata', 'pickle', 'copyreg', 'copy',
            'pprint', 'reprlib', 'enum', 'numbers', 'decimal', 'fractions',
            'contextvars', 'abc', 'atexit', 'traceback', 'gc', 'inspect',
            'site', 'warnings', 'dataclasses', 'typing', 'types', 'weakref',
            'ctypes', '_thread', 'thread', 'queue', 'asyncio', 'concurrent',
            'multiprocessing', 'dummy_threading', 'ssl', 'socket', 'email',
            'http', 'urllib', 'html', 'xml', 'webbrowser', 'cgi', 'cgitb',
            'wsgiref', 'uuid', 'socketserver', 'xmlrpc', 'ipaddress'
        }
        return module_name in stdlib_modules
    
    def _install_package(self, package_name: str) -> bool:
        """安装包"""
        try:
            # 处理特殊包名映射
            package_map = {
                'websocket': 'websocket-client',
                'PIL': 'Pillow',
                'cv2': 'opencv-python'
            }
            
            actual_package = package_map.get(package_name, package_name)
            
            # 使用pip安装包
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', actual_package],
                capture_output=True,
                text=True,
                timeout=120  # 2分钟超时
            )
            return result.returncode == 0
        except Exception:
            return False