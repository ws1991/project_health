# quick_diagnostic.py
import sys
import os

print("🚀 快速系统诊断")
print("=" * 50)

# 1. 检查环境
print("1. 环境检查:")
print(f"   Python路径: {sys.executable}")
print(f"   工作目录: {os.getcwd()}")

# 2. 检查依赖
print("\n2. 依赖检查:")
try:
    import pandas
    print(f"   ✅ pandas: {pandas.__version__}")
except:
    print("   ❌ pandas")

try:
    import langchain
    print(f"   ✅ langchain: {langchain.__version__}")
except:
    print("   ❌ langchain")

# 3. 尝试导入
print("\n3. 导入测试:")
try:
    sys.path.insert(0, '.')
    from agent import tools
    print("   ✅ agent.tools 导入成功")
    
    # 测试函数
    tools.test_constitutional_compliance()
    
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)