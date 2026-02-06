import matplotlib

print("🔍 查看 matplotlib 默认设置：")
print(f"默认 font.family: {matplotlib.rcParamsDefault['font.family']}")
print(f"默认 font.sans-serif: {matplotlib.rcParamsDefault['font.sans-serif'][:3]}")

print("\n📋 当前设置：")
print(f"当前 font.family: {matplotlib.rcParams['font.family']}")
print(f"当前 font.sans-serif: {matplotlib.rcParams['font.sans-serif'][:3]}")