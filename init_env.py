#!/usr/bin/env python3
"""
环境初始化脚本 - 运行一次即可
"""
import matplotlib
import matplotlib.pyplot as plt
import warnings
import platform
import json
from pathlib import Path

def setup_matplotlib_config():
    """设置matplotlib配置文件"""
    
    # 1. 获取matplotlib配置目录
    mpl_config_dir = Path(matplotlib.get_configdir())
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 创建matplotlibrc文件
    rc_file = mpl_config_dir / 'matplotlibrc'
    
    # 3. 根据操作系统配置
    system = platform.system()
    
    if system == 'Windows':
        font_config = """
# 字体设置
font.family : sans-serif
font.sans-serif : Microsoft YaHei, SimHei, Arial Unicode MS, DejaVu Sans, Arial, sans-serif
axes.unicode_minus : False

# 图形设置
figure.figsize : 12, 8
figure.autolayout : True
savefig.dpi : 300
savefig.bbox : tight

# 文本设置
legend.fontsize : 10
axes.titlesize : 14
axes.labelsize : 12
xtick.labelsize : 10
ytick.labelsize : 10

# 网格设置
grid.alpha : 0.3
"""
    else:
        font_config = """
# 字体设置
font.family : sans-serif
font.sans-serif : DejaVu Sans, Arial Unicode MS, Arial, Liberation Sans, sans-serif
axes.unicode_minus : False

# 图形设置
figure.figsize : 12, 8
figure.autolayout : True
savefig.dpi : 300
savefig.bbox : tight

# 文本设置
legend.fontsize : 10
axes.titlesize : 14
axes.labelsize : 12
xtick.labelsize : 10
ytick.labelsize : 10

# 网格设置
grid.alpha : 0.3
"""
    
    # 4. 写入配置文件
    with open(rc_file, 'w', encoding='utf-8') as f:
        f.write(font_config)
    
    print(f"✅ Matplotlib配置文件已创建: {rc_file}")
    print(f"   系统: {system}")
    
    # 5. 创建项目配置文件
    project_config = {
        "matplotlib_config": str(rc_file),
        "system": system,
        "font_family": "sans-serif" if system == "Windows" else "DejaVu Sans",
        "setup_complete": True
    }
    
    config_file = Path(".project_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(project_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 项目配置文件已创建: {config_file}")
    
    # 6. 测试配置
    print("\n🔧 测试配置...")
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("测试图表 - 中文测试")
    plt.xlabel("X轴")
    plt.ylabel("Y轴")
    plt.grid(True)
    
    test_file = "output/font_test.png"
    Path("output").mkdir(exist_ok=True)
    plt.savefig(test_file, dpi=150)
    print(f"✅ 测试图表已保存: {test_file}")
    
    plt.show()
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("环境初始化工具")
    print("="*60)
    
    setup_matplotlib_config()
    
    print("\n" + "="*60)
    print("初始化完成！")
    print("现在所有分析脚本都会使用这些字体设置。")
    print("="*60)