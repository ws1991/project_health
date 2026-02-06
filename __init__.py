#!/usr/bin/env python3
"""
睡眠健康分析项目 - 主入口文件
"""
import sys
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("="*60)
    print("睡眠健康数据分析系统")
    print("="*60)
    print("\n请选择分析模式:")
    print("1. 🚀 快速分析 (快速查看数据)")
    print("2. 📊 完整分析 (生成详细报告)")
    print("3. 🎯 命令行运行")
    print("4. ❓ 帮助")
    print("0. 🔚 退出")
    print("="*60)
    
    choice = input("\n请输入选项编号 (0-4): ").strip()
    
    if choice == "1":
        print("\n运行快速分析...")
        # 直接调用脚本
        subprocess.run([sys.executable, "scripts/quick_analysis.py"])
    
    elif choice == "2":
        print("\n运行完整分析...")
        subprocess.run([sys.executable, "scripts/analyze_sleep_health.py"])
    
    elif choice == "3":
        print("\n直接在命令行中运行:")
        print("快速分析: python scripts/quick_analysis.py")
        print("完整分析: python scripts/analyze_sleep_health.py")
        print("\n或使用参数:")
        print("python scripts/quick_analysis.py --data 你的数据文件.csv")
    
    elif choice == "4":
        show_help()
    
    elif choice == "0":
        print("\n感谢使用，再见！")
        sys.exit(0)
    
    else:
        print(f"\n❌ 无效选项: {choice}")
        print("请输入0-4之间的数字")

def show_help():
    """显示帮助信息"""
    help_text = """
使用说明:
=========

1. 确保数据文件在 data/raw/sleep_health_data.csv
2. 或使用命令行参数指定文件:
   python scripts/quick_analysis.py --data 你的文件.csv

常用命令:
========
# 快速分析
python scripts/quick_analysis.py

# 完整分析
python scripts/analyze_sleep_health.py

# 查看帮助
python scripts/quick_analysis.py --help
"""
    print(help_text)

if __name__ == "__main__":
    main()