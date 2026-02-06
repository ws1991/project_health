#!/usr/bin/env python3
"""
一键启动脚本 - 最简单的方式
"""
import os
import sys
from pathlib import Path

print("="*60)
print("健康数据分析系统启动")
print("="*60)

# 检查health.csv文件
data_file = "data/raw/health.csv"
if not Path(data_file).exists():
    print(f"❌ 找不到数据文件: {data_file}")
    print("\n请将你的 health.csv 文件放在 data/raw/ 目录下")
    print("当前 data/raw/ 目录内容:")
    
    data_dir = Path("data/raw")
    if data_dir.exists():
        for file in data_dir.glob("*"):
            print(f"  📄 {file.name}")
    else:
        print("  📁 data/raw/ 目录不存在")
    
    # 询问是否要创建目录结构
    print("\n是否要创建项目目录结构? (y/n): ")
    choice = input().strip().lower()
    if choice == 'y':
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        print("✅ 目录创建完成")
        print(f"请将 health.csv 文件复制到 {data_file}")
    input("\n按 Enter 键退出...")
    sys.exit(1)

# 检查依赖
print("\n📦 检查Python依赖...")
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    print("✅ 所有依赖已安装")
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请运行: pip install pandas numpy matplotlib seaborn")
    input("\n按 Enter 键退出...")
    sys.exit(1)

# 创建输出目录
Path("output").mkdir(exist_ok=True)

# 运行快速分析
print("\n🚀 开始快速分析...")
print("="*50)

# 直接执行quick_analysis.py
script_path = "scripts/quick_analysis.py"
if Path(script_path).exists():
    try:
        # 读取并执行脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 创建执行环境
        exec_env = {
            '__name__': '__main__',
            '__file__': script_path,
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'Path': Path,
            'sys': sys,
            'os': os
        }
        
        # 导入必要的模块
        import re
        exec_env['re'] = re
        
        # 执行脚本
        exec(script_content, exec_env)
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ 脚本不存在: {script_path}")
    print("正在使用内置分析...")
    
    # 如果脚本不存在，直接运行分析
    from scripts.quick_analysis import main as quick_main
    quick_main()

print("="*50)
input("\n🎉 分析完成！按 Enter 键退出...")