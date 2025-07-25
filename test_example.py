#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版测试脚本 - 用于演示Python转EXE功能
"""

import os
import sys
import time
import json
from datetime import datetime


class SimpleApp:
    """简单的应用程序类"""
    
    def __init__(self):
        self.name = "Python to EXE Test App"
        self.version = "1.0.0"
        self.start_time = datetime.now()
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            'platform': sys.platform,
            'python_version': sys.version,
            'current_dir': os.getcwd(),
            'executable': sys.executable,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def run(self):
        """运行应用程序"""
        # 设置控制台编码为UTF-8以支持Unicode字符
        if sys.platform == 'win32':
            import locale
            try:
                # 尝试设置控制台代码页为UTF-8
                import ctypes
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)
                ctypes.windll.kernel32.SetConsoleCP(65001)
            except:
                pass
        
        try:
            print(f"🚀 {self.name} v{self.version}")
            print("=" * 50)
            
            # 获取系统信息
            info = self.get_system_info()
            print("📊 系统信息:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            print("\n⏰ 开始执行任务...")
            
            # 模拟一些处理
            for i in range(5):
                print(f"  步骤 {i+1}/5: 正在处理...")
                time.sleep(1)
            
            print("\n✅ 任务执行完成!")
            
            # 保存结果到文件
            result_file = "execution_result.json"
            result = {
                'app_name': self.name,
                'version': self.version,
                'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success',
                'system_info': info
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"📁 结果已保存到: {result_file}")
            
        except UnicodeEncodeError:
            # If Unicode characters cannot be displayed, use ASCII alternatives
            print(f">> Python to EXE Test App v{self.version}")
            print("=" * 50)
            
            info = self.get_system_info()
            print(">> System Info:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            print("\n>> Starting tasks...")
            
            for i in range(5):
                print(f"  Step {i+1}/5: Processing...")
                time.sleep(1)
            
            print("\n>> Tasks completed!")
            
            result_file = "execution_result.json"
            result = {
                'app_name': 'Python to EXE Test App',
                'version': self.version,
                'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success',
                'system_info': info
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f">> Results saved to: {result_file}")
        
        # Wait for user input (if console is available)
        try:
            input("\nPress Enter to exit...")
        except:
            # If no console, wait 3 seconds before exit
            time.sleep(3)


def main():
    """Main function"""
    app = SimpleApp()
    app.run()


if __name__ == '__main__':
    main()