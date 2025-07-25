import os
import sys
import json
import subprocess
import tempfile
import shutil
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