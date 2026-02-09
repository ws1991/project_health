#!/usr/bin/env python
"""
项目设置诊断
"""
import os
import sys

def check_setup():
    print("🔍 项目设置检查")
    print("=" * 50)
    
    checks = []
    
    # 1. 文件检查
    files = [
        ('config/secrets.yaml', '配置文件'),
        ('agent/orchestrator.py', '智能体核心'),
        ('agent/tools.py', '工具集'),
        ('ai/hybrid_client.py', 'AI客户端'),
        ('interactive_agent.py', '交互程序'),
    ]
    
    for file, desc in files:
        exists = os.path.exists(file)
        checks.append((f"文件: {desc}", exists))
        print(f"{'✅' if exists else '❌'} {desc}: {file}")
    
    # 2. 目录检查
    dirs = [
        ('data/raw', '原始数据目录'),
        ('output/figures', '图表输出目录'),
        ('output/reports', '报告输出目录'),
    ]
    
    for dir_path, desc in dirs:
        exists = os.path.exists(dir_path)
        checks.append((f"目录: {desc}", exists))
        print(f"{'✅' if exists else '❌'} {desc}: {dir_path}")
    
    # 总结
    print("\n" + "=" * 50)
    passed = sum(1 for _, success in checks if success)
    total = len(checks)
    
    print(f"📊 检查结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有检查通过！可以运行: python interactive_agent.py")
    else:
        print("⚠️  存在缺失文件或目录")
        print("\n请创建缺失的文件:")
        for (item, success) in checks:
            if not success:
                print(f"  - {item}")

if __name__ == "__main__":
    check_setup()