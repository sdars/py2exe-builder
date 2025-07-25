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
        self.name = "Python转EXE测试应用"
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
        
        # 等待用户输入（如果有控制台）
        try:
            input("\n按回车键退出...")
        except:
            # 如果没有控制台，等待3秒后退出
            time.sleep(3)


def main():
    """主函数"""
    app = SimpleApp()
    app.run()


if __name__ == '__main__':
    main()