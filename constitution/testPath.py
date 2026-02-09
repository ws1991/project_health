# 修复的测试脚本
import sys
from pathlib import Path

constitution_path = Path("constitution")
print("📁 宪法系统模块结构：")
for item in constitution_path.rglob("*"):
    if item.is_file() and item.suffix in ['.py', '.yaml', '.yml']:
        rel_path = str(item.relative_to(constitution_path))  # 转换为字符串
        size_kb = item.stat().st_size / 1024
        print(f"  {rel_path:<40} {size_kb:5.1f} KB")