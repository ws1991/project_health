"""
全局字体配置 - 增强版
"""
import matplotlib
import matplotlib.pyplot as plt
import warnings
import platform
import json
import os
from pathlib import Path
import sys

def setup_global_fonts():
    """
    全局字体设置函数 - 强制生效
    """
    print("🔤 设置全局字体配置...")
    
    # 1. 完全忽略所有警告
    warnings.filterwarnings('ignore')
    
    # 2. 重新加载matplotlib配置
    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    
    # 3. 根据操作系统设置字体
    system = platform.system()
    
    if system == 'Windows':
        font_list = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 
                    'DejaVu Sans', 'Arial', 'sans-serif']
    elif system == 'Darwin':
        font_list = ['PingFang SC', 'Heiti SC', 'Arial Unicode MS',
                    'DejaVu Sans', 'Arial', 'sans-serif']
    else:
        font_list = ['DejaVu Sans', 'Arial Unicode MS', 'Arial',
                    'Liberation Sans', 'sans-serif']
    
    # 4. 强制设置所有相关参数
    rc_params = {
        # 字体设置
        'font.family': 'sans-serif',
        'font.sans-serif': font_list,
        'axes.unicode_minus': False,
        
        # 图形设置
        'figure.figsize': (12, 8),
        'figure.autolayout': True,
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.format': 'png',
        
        # 文本设置
        'legend.fontsize': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'font.size': 11,
        
        # 网格设置
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
        
        # 线条设置
        'lines.linewidth': 2,
        'lines.markersize': 8,
        
        # 其他设置
        'image.cmap': 'viridis',
        'axes.grid': True,
    }
    
    # 5. 应用配置
    matplotlib.rcParams.update(rc_params)
    
    # 6. 尝试加载字体文件（Windows专用）
    if system == 'Windows':
        try:
            import matplotlib.font_manager as fm
            
            # Windows常见字体路径
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
                'C:/Windows/Fonts/simhei.ttf',    # 黑体
                'C:/Windows/Fonts/simsun.ttc',    # 宋体
                'C:/Windows/Fonts/msjhl.ttc',     # 微软正黑
            ]
            
            for font_path in font_paths:
                font_file = Path(font_path)
                if font_file.exists():
                    try:
                        fm.fontManager.addfont(str(font_file))
                        font_prop = fm.FontProperties(fname=str(font_file))
                        font_name = font_prop.get_name()
                        print(f"✅ 加载字体文件: {font_name}")
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"⚠️  字体文件加载失败: {e}")
    
    # 7. 验证字体
    available_fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
    
    # 检查是否有所需字体
    found_fonts = []
    for font in font_list:
        if font in available_fonts:
            found_fonts.append(font)
    
    if found_fonts:
        print(f"✅ 可用字体: {found_fonts[:3]}...")
        # 使用第一个找到的字体
        matplotlib.rcParams['font.sans-serif'] = [found_fonts[0]] + font_list
    else:
        print("⚠️  未找到中文字体，使用默认字体")
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    
    # 8. 保存配置到项目文件（用于调试）
    config_data = {
        'system': system,
        'font_list': font_list,
        'available_fonts': available_fonts[:10],  # 只保存前10个
        'rc_params_applied': list(rc_params.keys()),
        'timestamp': str(Path(__file__).stat().st_mtime)
    }
    
    config_file = Path(".font_config_debug.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 字体配置完成 (系统: {system})")
    print(f"   配置文件: {config_file}")
    
    # 9. 测试配置
    test_configuration()
    
    return True

def test_configuration():
    """测试当前配置"""
    try:
        import matplotlib.pyplot as plt
        
        # 创建测试图表
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 9], 'ro-', label='测试线')
        ax.set_title('字体测试 - 中文标题', fontsize=12)
        ax.set_xlabel('X轴标签')
        ax.set_ylabel('Y轴标签')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存测试图
        test_dir = Path("output/tests")
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / "font_config_test.png"
        fig.savefig(test_file, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"✅ 配置测试完成: {test_file}")
        return True
        
    except Exception as e:
        print(f"⚠️  配置测试失败: {e}")
        return False

# 自动执行
if __name__ == "__main__":
    setup_global_fonts()
else:
    # 作为模块导入时自动执行
    setup_global_fonts()