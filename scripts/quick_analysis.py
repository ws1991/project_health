#!/usr/bin/env python3
"""
快速分析脚本
"""

# ============== 1. 导入所有需要的模块 ==============
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore')

# 基础模块
import sys
from pathlib import Path
import pandas as pd  # ✅ 这里导入 pandas
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import platform
import os
import matplotlib
from matplotlib import font_manager
import re


# ===================================================

# 现在所有函数都可以使用 pd, plt, np 等

def load_health_data(data_path=None):
    """加载health.csv数据"""
    if data_path is None:
        data_path = "data/raw/health.csv"
    
    if not Path(data_path).exists():
        print(f"❌ 文件不存在: {data_path}")
        print("请将 health.csv 文件放在 data/raw/ 目录下")
        return None
    
    try:
        df = pd.read_csv(data_path, encoding='utf-8')
        print(f"✅ 成功加载数据: {df.shape[0]}行 × {df.shape[1]}列")
        return df
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return None

def parse_chinese_datetime(date_str):
    """解析中文格式的日期"""
    try:
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', str(date_str))
        if date_match:
            year, month, day = map(int, date_match.groups())
            return pd.Timestamp(year=year, month=month, day=day)
    except:
        return pd.NaT
    return pd.NaT

def extract_time(datetime_str):
    """从日期时间字符串中提取时间（小时）"""
    try:
        match = re.search(r'(\d{1,2}):(\d{2})', str(datetime_str))
        if match:
            hour, minute = map(int, match.groups())
            return hour + minute/60
    except:
        return np.nan
    return np.nan

def calculate_sleep_duration(sleep_hour, wake_hour):
    """计算睡眠时长，处理跨夜情况"""
    if pd.isna(sleep_hour) or pd.isna(wake_hour):
        return np.nan
    
    if wake_hour > sleep_hour:
        return wake_hour - sleep_hour
    else:
        return wake_hour + 24 - sleep_hour

def analyze_data(df):
    import matplotlib.pyplot as plt

    """执行数据分析"""
    print("\n🔍 开始数据分析...")
    
    # 解析时间
    df['parsed_date'] = df['date'].apply(parse_chinese_datetime)
    df['sleep_hour'] = df['sleep'].apply(extract_time)
    df['wake_hour'] = df['getup'].apply(extract_time)
    
    # 计算睡眠时长
    df['sleep_duration'] = df.apply(
        lambda row: calculate_sleep_duration(row['sleep_hour'], row['wake_hour']), 
        axis=1
    )
    
    # 创建输出目录
    Path("output").mkdir(exist_ok=True)
    
    # 创建图表
    create_visualizations(df)
    
    # 打印统计摘要
    print_statistics(df)
    
    # 保存处理后的数据
    df.to_csv("output/processed_health_data.csv", index=False, encoding='utf-8')
    print(f"\n💾 处理后的数据已保存: output/processed_health_data.csv")
    
    return df

def create_visualizations(df):

    """创建可视化图表"""
    print("📊 生成图表...")
    
    import matplotlib.pyplot as plt
    import matplotlib
    
    # ============ 关键诊断 ============
    print("🔍 关键诊断信息:")
    print(f"1. 当前字体设置: {matplotlib.rcParams['font.sans-serif'][:3]}")
    print(f"2. 后端: {matplotlib.get_backend()}")
    print(f"3. 数据形状: {df.shape if hasattr(df, 'shape') else '无数据'}")
    
    # 立即测试中文显示
    try:
        fig_test, ax_test = plt.subplots(figsize=(6, 4))
        test_texts = [
            "Microsoft YaHei测试",
            "癫痫发作分析",
            "日期: 2024年",
            "程度: 中度"
        ]
        
        for i, text in enumerate(test_texts):
            ax_test.text(0.5, 0.7 - i*0.15, text, 
                        fontsize=12, ha='center', va='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        ax_test.set_xlim(0, 1)
        ax_test.set_ylim(0, 1)
        ax_test.axis('off')
        
        plt.tight_layout()
        test_file = "output/immediate_font_test.png"
        plt.savefig(test_file, dpi=150, bbox_inches='tight')
        plt.close(fig_test)
        
        print(f"✅ 即时字体测试图已保存: {test_file}")
        print("   请立即打开查看中文是否显示")
        
    except Exception as e:
        print(f"❌ 字体测试失败: {e}")
        
    # 使用matplotlib默认样式，但自定义一些参数


    # =================================
    print("📊 生成图表...")
    
    # 设置图表风格
    #plt.style.use('seaborn-v0_8')
    
    # 创建多子图
    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    
    # 图表1: 癫痫发作趋势
    axes[0, 0].plot(df['parsed_date'], df['seizure'], marker='o', color='red', 
                   alpha=0.7, linewidth=2)
    axes[0, 0].set_title('癫痫发作趋势', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('日期')
    axes[0, 0].set_ylabel('发作程度')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 图表2: 睡眠时长趋势
    axes[0, 1].plot(df['parsed_date'], df['sleep_duration'], marker='s', 
                   color='blue', alpha=0.7, linewidth=2)
    axes[0, 1].set_title('睡眠时长趋势', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('日期')
    axes[0, 1].set_ylabel('睡眠时长(小时)')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 图表3: 步数趋势
    axes[0, 2].plot(df['parsed_date'], df['step'], marker='^', color='green', 
                   alpha=0.7, linewidth=2)
    axes[0, 2].set_title('步数趋势', fontsize=14, fontweight='bold')
    axes[0, 2].set_xlabel('日期')
    axes[0, 2].set_ylabel('步数')
    axes[0, 2].grid(True, alpha=0.3)
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # 图表4: 癫痫发作与睡眠时长关系
    scatter1 = axes[1, 0].scatter(df['sleep_duration'], df['seizure'], 
                                c=df['seizure'], cmap='Reds', 
                                alpha=0.7, s=80, edgecolors='black')
    axes[1, 0].set_title('发作 vs 睡眠时长', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('睡眠时长(小时)')
    axes[1, 0].set_ylabel('发作程度')
    axes[1, 0].grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=axes[1, 0], label='发作强度')
    
    # 图表5: 癫痫发作与步数关系
    scatter2 = axes[1, 1].scatter(df['step'], df['seizure'], 
                                c=df['seizure'], cmap='Reds', 
                                alpha=0.7, s=80, edgecolors='black')
    axes[1, 1].set_title('发作 vs 步数', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('步数')
    axes[1, 1].set_ylabel('发作程度')
    axes[1, 1].grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=axes[1, 1], label='发作强度')
    
    # 图表6: 锻炼强度分布
    if 'exercise' in df.columns:
        exercise_counts = df['exercise'].value_counts().sort_index()
        colors = plt.cm.Set3(np.linspace(0, 1, len(exercise_counts)))
        axes[1, 2].bar(exercise_counts.index, exercise_counts.values, 
                      color=colors, alpha=0.8, edgecolor='black')
        axes[1, 2].set_title('锻炼强度分布', fontsize=14, fontweight='bold')
        axes[1, 2].set_xlabel('锻炼强度')
        axes[1, 2].set_ylabel('天数')
        axes[1, 2].grid(True, alpha=0.3, axis='y')
    
    # 图表7: 睡眠时长分布
    axes[2, 0].hist(df['sleep_duration'].dropna(), bins=15, 
                   color='skyblue', edgecolor='black', alpha=0.7)
    axes[2, 0].set_title('睡眠时长分布', fontsize=14, fontweight='bold')
    axes[2, 0].set_xlabel('睡眠时长(小时)')
    axes[2, 0].set_ylabel('频数')
    axes[2, 0].grid(True, alpha=0.3, axis='y')
    
    # 图表8: 步数分布
    axes[2, 1].hist(df['step'].dropna(), bins=15, 
                   color='lightgreen', edgecolor='black', alpha=0.7)
    axes[2, 1].set_title('步数分布', fontsize=14, fontweight='bold')
    axes[2, 1].set_xlabel('步数')
    axes[2, 1].set_ylabel('频数')
    axes[2, 1].grid(True, alpha=0.3, axis='y')
    
    # 图表9: 相关性热图
    numeric_cols = ['seizure', 'sleep_duration', 'step', 'exercise']
    numeric_df = df[numeric_cols].dropna()
    
    if len(numeric_df) > 1:
        corr_matrix = numeric_df.corr()
        im = axes[2, 2].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        axes[2, 2].set_title('特征相关性热图', fontsize=14, fontweight='bold')
        axes[2, 2].set_xticks(range(len(numeric_cols)))
        axes[2, 2].set_yticks(range(len(numeric_cols)))
        axes[2, 2].set_xticklabels(numeric_cols, rotation=45)
        axes[2, 2].set_yticklabels(numeric_cols)
        
        # 添加数值标签
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                text = axes[2, 2].text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                                     ha="center", va="center", 
                                     color="white", fontweight='bold')
        
        plt.colorbar(im, ax=axes[2, 2])
    
    plt.tight_layout()
    
    # 保存图表
    output_path = "output/health_analysis_report.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📸 图表已保存: {output_path}")
    
    # 显示图表
    plt.show()

def print_statistics(df):
    """打印统计摘要"""
    print("\n" + "="*60)
    print("📈 健康数据统计摘要")
    print("="*60)
    
    # 基本信息
    print(f"📅 数据期间: {df['parsed_date'].min().date()} 到 {df['parsed_date'].max().date()}")
    print(f"📊 总天数: {len(df)}")
    
    # 癫痫发作统计
    if 'seizure' in df.columns:
        seizure_stats = df['seizure'].describe()
        seizure_days = (df['seizure'] > 0).sum()
        print(f"\n⚡ 癫痫发作统计:")
        print(f"  - 有发作天数: {seizure_days} ({seizure_days/len(df)*100:.1f}%)")
        print(f"  - 平均发作强度: {seizure_stats['mean']:.2f}")
        print(f"  - 最大发作强度: {seizure_stats['max']:.0f}")
        print(f"  - 最小发作强度: {seizure_stats['min']:.0f}")
    
    # 睡眠统计
    if 'sleep_duration' in df.columns:
        sleep_stats = df['sleep_duration'].describe()
        print(f"\n😴 睡眠统计:")
        print(f"  - 平均睡眠时长: {sleep_stats['mean']:.1f}小时")
        print(f"  - 最长睡眠: {sleep_stats['max']:.1f}小时")
        print(f"  - 最短睡眠: {sleep_stats['min']:.1f}小时")
        
        # 睡眠分类
        short_sleep = (df['sleep_duration'] < 7).sum()
        normal_sleep = ((df['sleep_duration'] >= 7) & (df['sleep_duration'] <= 9)).sum()
        long_sleep = (df['sleep_duration'] > 9).sum()
        
        print(f"  - 睡眠不足(<7h): {short_sleep}天 ({short_sleep/len(df)*100:.1f}%)")
        print(f"  - 正常睡眠(7-9h): {normal_sleep}天 ({normal_sleep/len(df)*100:.1f}%)")
        print(f"  - 睡眠过多(>9h): {long_sleep}天 ({long_sleep/len(df)*100:.1f}%)")
    
    # 步数统计
    if 'step' in df.columns:
        step_stats = df['step'].describe()
        print(f"\n🚶 步数统计:")
        print(f"  - 平均步数: {step_stats['mean']:.0f}")
        print(f"  - 最高步数: {step_stats['max']:.0f}")
        print(f"  - 最低步数: {step_stats['min']:.0f}")
        
        # 活动水平分类
        sedentary = (df['step'] < 3000).sum()
        moderate = ((df['step'] >= 3000) & (df['step'] < 7500)).sum()
        active = (df['step'] >= 7500).sum()
        
        print(f"  - 久坐(<3000步): {sedentary}天 ({sedentary/len(df)*100:.1f}%)")
        print(f"  - 中等活动(3000-7499步): {moderate}天 ({moderate/len(df)*100:.1f}%)")
        print(f"  - 活跃(≥7500步): {active}天 ({active/len(df)*100:.1f}%)")
    
    # 锻炼统计
    if 'exercise' in df.columns:
        exercise_stats = df['exercise'].describe()
        exercise_days = (df['exercise'] > 0).sum()
        print(f"\n💪 锻炼统计:")
        print(f"  - 锻炼天数: {exercise_days} ({exercise_days/len(df)*100:.1f}%)")
        print(f"  - 平均锻炼强度: {exercise_stats['mean']:.2f}")
        print(f"  - 最大锻炼强度: {exercise_stats['max']:.0f}")
    
    # 相关性分析
    print(f"\n🔗 相关性分析:")
    if 'seizure' in df.columns and 'sleep_duration' in df.columns:
        sleep_corr = df['seizure'].corr(df['sleep_duration'])
        if not pd.isna(sleep_corr):
            print(f"  - 癫痫发作 vs 睡眠时长: {sleep_corr:.3f}")
    
    if 'seizure' in df.columns and 'step' in df.columns:
        step_corr = df['seizure'].corr(df['step'])
        if not pd.isna(step_corr):
            print(f"  - 癫痫发作 vs 步数: {step_corr:.3f}")
    
    if 'seizure' in df.columns and 'exercise' in df.columns:
        exercise_corr = df['seizure'].corr(df['exercise'])
        if not pd.isna(exercise_corr):
            print(f"  - 癫痫发作 vs 锻炼强度: {exercise_corr:.3f}")
    
    print("="*60)

def generate_recommendations(df):
    """生成健康建议"""
    print("\n💡 健康建议:")
    
    # 睡眠建议
    if 'sleep_duration' in df.columns:
        avg_sleep = df['sleep_duration'].mean()
        if avg_sleep < 7:
            print("- 💤 您的平均睡眠时长不足7小时，建议增加睡眠时间")
        elif avg_sleep > 9:
            print("- 💤 您的睡眠时长可能过多，建议保持7-9小时")
        else:
            print("- 💤 您的睡眠时长在理想范围内，继续保持")
    
    # 活动建议
    if 'step' in df.columns:
        avg_steps = df['step'].mean()
        if avg_steps < 5000:
            print("- 🚶 每日平均步数低于5000步，建议增加日常活动量")
        elif avg_steps < 7500:
            print("- 🚶 您的活动量适中，可以考虑增加到7500步以上")
        else:
            print("- 🚶 您的活动量充足，继续保持")
    
    # 癫痫管理建议
    if 'seizure' in df.columns and (df['seizure'] > 0).any():
        print("- ⚠️  监测到癫痫发作记录，请密切观察并与医生保持沟通")
    
    print()

def main():
    import sys
    from pathlib import Path
    global matplotlib  # ✅ 声明使用全局变量
    global font_manager  # ✅ 声明使用全局变量

    """主函数"""
    # ============== 使用已验证成功的字体设置 ==============
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    
    import matplotlib
    from matplotlib import font_manager
    import platform
    import os
    
    print("🎨 应用已验证的中文字体设置...")
    
    # 1. 清除字体缓存（关键步骤！）
    try:
        font_manager._load_fontmanager(try_read_cache=False)
        print("✅ 字体缓存已清除")
    except:
        try:
            cache_file = font_manager.fontManager.cache_file
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print("✅ 删除字体缓存文件")
        except:
            print("⚠️  无法清除字体缓存")
    
    # 2. 使用已验证成功的字体列表
    font_list = [
        'Microsoft YaHei',  # ✅ 已验证可用
        'SimHei',           # 黑体
        'KaiTi',            # 楷体
        'SimSun',           # 宋体
        'STSong',           # 华文宋体
        'DejaVu Sans',      # 后备
        'Arial'             # 最后后备
    ]
    
    # 3. 应用字体设置
    matplotlib.rcParams.update({
        'font.sans-serif': font_list,
        'axes.unicode_minus': False,
    })
    
    print(f"✅ 使用字体: {font_list[0]}")
    print("="*60)
    # ===================================================
    test_font_application()
    # ====================================================
    
    # 忽略警告
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    print("✅ 配置导入完成")
    """主函数"""
    print("="*60)
    print("健康数据分析工具 - 快速分析")
    print("="*60)
    
    # 检查数据文件
    data_path = "data/raw/health.csv"
    
    if not Path(data_path).exists():
        print(f"❌ 找不到数据文件: {data_path}")
        print("请将 health.csv 文件放在 data/raw/ 目录下")
        print("\n当前目录结构:")
        for path in Path(".").glob("*"):
            print(f"  {'📁' if path.is_dir() else '📄'} {path.name}")
        return
    
    # 加载和分析数据
    df = load_health_data(data_path)

    if df is not None:
        df = analyze_data(df)
        generate_recommendations(df)
        print("\n✅ 分析完成！")
        print("📁 结果保存在 output/ 目录")
        print("📊 查看图表: output/health_analysis_report.png")
        print("📄 查看数据: output/processed_health_data.csv")
# 在生成第一个图表前，添加这个测试

def test_font_application():
    """测试字体是否真的应用到图表"""
    import matplotlib.pyplot as plt
    
    print("🔍 测试字体应用...")
    
    # 创建最简单的测试图
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # 使用多种中文文本
    test_texts = [
        "Microsoft YaHei测试",
        "发作程度分析",
        "睡眠时长记录",
        "日期范围统计"
    ]
    
    for i, text in enumerate(test_texts):
        ax.text(0.5, 0.8 - i*0.2, text, 
                fontsize=12, 
                ha='center',
                transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # 保存并立即显示信息
    test_file = "font_application_test.png"
    plt.savefig(test_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 字体应用测试图已保存: {test_file}")
    
    # 验证文件是否存在
    import os
    if os.path.exists(test_file):
        print(f"   文件大小: {os.path.getsize(test_file)} 字节")
        return True
    else:
        print("❌ 测试图未生成")
        return False

if __name__ == "__main__":
    main()