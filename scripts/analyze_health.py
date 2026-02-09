#!/usr/bin/env python
"""
健康数据分析脚本 - 独立可运行版本
保存为：scripts/health_analysis.py
"""
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
import sys

def load_health_data(file_path):
    """加载健康数据CSV文件"""
    print(f"📂 正在加载数据: {file_path}")
    
    try:
        # 读取CSV
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"✅ 加载成功: {len(df)}行, {len(df.columns)}列")
        print(f"   列名: {list(df.columns)}")
        
        # 标准化列名
        df.columns = [col.strip().lower() for col in df.columns]
        
        # 解析日期
        if 'date' in df.columns:
            try:
                df['date_parsed'] = pd.to_datetime(df['date'], format='%Y年%m月%d日', errors='coerce')
                valid_dates = df['date_parsed'].dropna()
                if len(valid_dates) > 0:
                    print(f"✅ 日期解析成功: {valid_dates.min().date()} 至 {valid_dates.max().date()}")
            except Exception as e:
                print(f"⚠️  日期解析失败: {e}")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        print(f"   请确保文件路径正确")
        return None
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return None

def parse_chinese_time(time_str):
    """解析中文格式的时间"""
    try:
        if pd.isna(time_str):
            return pd.NaT
        
        time_str = str(time_str)
        # 移除时区信息
        if '(' in time_str:
            time_part = time_str.split('(')[0].strip()
        else:
            time_part = time_str
        
        # 尝试两种格式
        for fmt in ['%Y年%m月%d日 %H:%M', '%Y年%m月%d日']:
            try:
                return datetime.strptime(time_part, fmt)
            except:
                continue
        return pd.NaT
    except:
        return pd.NaT

def calculate_sleep_duration(df):
    """计算睡眠时长"""
    if 'sleep' in df.columns and 'getup' in df.columns:
        df['sleep_time'] = df['sleep'].apply(parse_chinese_time)
        df['getup_time'] = df['getup'].apply(parse_chinese_time)
        
        # 计算睡眠时长
        mask = df['sleep_time'].notna() & df['getup_time'].notna()
        if mask.any():
            df.loc[mask, 'sleep_duration_hours'] = (
                (df.loc[mask, 'getup_time'] - df.loc[mask, 'sleep_time']).dt.total_seconds() / 3600
            )
            # 处理跨天睡眠
            df.loc[df['sleep_duration_hours'] < 0, 'sleep_duration_hours'] += 24
            
            sleep_data = df['sleep_duration_hours'].dropna()
            if len(sleep_data) > 0:
                print(f"✅ 睡眠时长计算完成")
                print(f"   平均睡眠: {sleep_data.mean():.1f}小时")
    
    return df

def analyze_basic_stats(df):
    """基础统计分析"""
    results = {}
    
    print("\n📊 基础统计分析:")
    print("=" * 40)
    
    # 发作程度分析
    if 'seizurescale' in df.columns:
        seizure_data = df['seizurescale'].dropna()
        if len(seizure_data) > 0:
            seizure_days = len(seizure_data[seizure_data > 0])
            seizure_rate = (seizure_days / len(seizure_data) * 100) if len(seizure_data) > 0 else 0
            
            results['seizure'] = {
                '总天数': len(seizure_data),
                '发作天数': seizure_days,
                '发作频率': f"{seizure_rate:.1f}%",
                '平均程度': float(seizure_data.mean()),
                '最大程度': int(seizure_data.max()),
                '程度分布': dict(seizure_data.value_counts().sort_index())
            }
            
            print(f"🔴 发作程度:")
            print(f"   • 发作频率: {seizure_rate:.1f}%")
            print(f"   • 平均程度: {seizure_data.mean():.2f}")
            print(f"   • 程度分布: {dict(seizure_data.value_counts().sort_index())}")
    
    # 睡眠分析
    if 'sleep_duration_hours' in df.columns:
        sleep_data = df['sleep_duration_hours'].dropna()
        if len(sleep_data) > 0:
            sleep_status = '良好' if 7 <= sleep_data.mean() <= 9 else '偏短' if sleep_data.mean() < 7 else '偏长'
            
            results['sleep'] = {
                '平均时长': float(sleep_data.mean()),
                '最短时长': float(sleep_data.min()),
                '最长时长': float(sleep_data.max()),
                '建议范围': '7-9小时',
                '评估': sleep_status
            }
            
            print(f"😴 睡眠时长:")
            print(f"   • 平均值: {sleep_data.mean():.1f}小时")
            print(f"   • 范围: {sleep_data.min():.1f}-{sleep_data.max():.1f}小时")
            print(f"   • 评估: {sleep_status}")
    
    # 步数分析
    if 'step' in df.columns:
        step_data = df['step'].dropna()
        if len(step_data) > 0:
            activity_level = '充足' if step_data.mean() >= 8000 else '中等' if step_data.mean() >= 5000 else '不足'
            
            results['step'] = {
                '平均步数': float(step_data.mean()),
                '最小步数': float(step_data.min()),
                '最大步数': float(step_data.max()),
                '目标': '8000-10000步',
                '评估': activity_level
            }
            
            print(f"👟 每日步数:")
            print(f"   • 平均值: {int(step_data.mean())}步")
            print(f"   • 范围: {int(step_data.min())}-{int(step_data.max())}步")
            print(f"   • 评估: {activity_level}")
    
    # 学习强度分析
    if 'study' in df.columns:
        study_data = df['study'].dropna()
        if len(study_data) > 0:
            study_status = '适中' if 1 <= study_data.mean() <= 2 else '较低' if study_data.mean() < 1 else '较高'
            
            results['study'] = {
                '平均强度': float(study_data.mean()),
                '评估': study_status
            }
            
            print(f"📚 学习强度:")
            print(f"   • 平均值: {study_data.mean():.1f}")
            print(f"   • 评估: {study_status}")
    
    return results

def create_basic_charts(df, save_dir='output/figures'):
    """创建基本图表"""
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    charts = []
    
    print(f"\n📈 正在生成图表...")
    
    try:
        # 1. 发作程度分布图
        if 'seizurescale' in df.columns:
            plt.figure(figsize=(10, 6))
            seizure_counts = df['seizurescale'].value_counts().sort_index()
            colors = ['green' if x == 0 else 'orange' if x == 1 else 'red' for x in seizure_counts.index]
            
            plt.bar([str(x) for x in seizure_counts.index], seizure_counts.values, 
                   color=colors, alpha=0.7, width=0.6)
            plt.title('发作程度分布', fontsize=14, fontweight='bold')
            plt.xlabel('发作程度 (0=无, 1=轻度, ≥2=中度以上)', fontsize=12)
            plt.ylabel('天数', fontsize=12)
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # 添加数值标签
            for i, v in enumerate(seizure_counts.values):
                plt.text(i, v + 0.1, str(v), ha='center', fontsize=10)
            
            chart_path = f"{save_dir}/seizure_distribution_{timestamp}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
            print(f"✅ 创建图表: 发作程度分布图 → {chart_path}")
    
    except Exception as e:
        print(f"⚠️  图表1创建失败: {e}")
    
    try:
        # 2. 睡眠时长分布图
        if 'sleep_duration_hours' in df.columns:
            sleep_data = df['sleep_duration_hours'].dropna()
            if len(sleep_data) > 0:
                plt.figure(figsize=(10, 6))
                
                plt.hist(sleep_data, bins=15, color='steelblue', alpha=0.7, 
                        edgecolor='black', linewidth=0.5)
                
                # 添加参考线
                plt.axvline(x=7, color='red', linestyle='--', linewidth=2, 
                           label='推荐值(7h)', alpha=0.8)
                plt.axvline(x=sleep_data.mean(), color='green', linestyle='-', 
                           linewidth=2, label=f'均值({sleep_data.mean():.1f}h)', alpha=0.8)
                
                plt.title('睡眠时长分布', fontsize=14, fontweight='bold')
                plt.xlabel('睡眠时长(小时)', fontsize=12)
                plt.ylabel('频次', fontsize=12)
                plt.legend()
                plt.grid(True, alpha=0.3, linestyle='--')
                
                chart_path = f"{save_dir}/sleep_distribution_{timestamp}.png"
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()
                charts.append(chart_path)
                print(f"✅ 创建图表: 睡眠时长分布图 → {chart_path}")
    
    except Exception as e:
        print(f"⚠️  图表2创建失败: {e}")
    
    return charts

def generate_report(stats, charts, file_path, save_dir='output/reports'):
    """生成分析报告"""
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"{save_dir}/analysis_report_{timestamp}.md"
    
    report = f"""# 健康数据分析报告

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**数据文件**: {file_path}

## 📊 核心发现

"""
    
    # 添加核心发现
    if 'seizure' in stats:
        seizure = stats['seizure']
        report += f"### 1. 发作情况\n"
        report += f"- **发作频率**: {seizure['发作频率']}\n"
        report += f"- **平均程度**: {seizure['平均程度']:.2f}\n"
        report += f"- **最严重程度**: {seizure['最大程度']}\n\n"
    
    if 'sleep' in stats:
        sleep = stats['sleep']
        report += f"### 2. 睡眠情况\n"
        report += f"- **平均睡眠**: {sleep['平均时长']:.1f}小时 ({sleep['评估']})\n"
        report += f"- **睡眠范围**: {sleep['最短时长']:.1f}-{sleep['最长时长']:.1f}小时\n\n"
    
    if 'step' in stats:
        step = stats['step']
        report += f"### 3. 活动情况\n"
        report += f"- **平均步数**: {int(step['平均步数'])}步 ({step['评估']})\n"
        report += f"- **步数范围**: {int(step['最小步数'])}-{int(step['最大步数'])}步\n\n"
    
    # 添加图表信息
    if charts:
        report += f"## 📈 可视化图表\n\n"
        for chart in charts:
            chart_name = os.path.basename(chart)
            report += f"- `{chart_name}`\n"
    
    # 添加建议
    report += f"""
## 💡 健康建议

### 基于数据的观察：
1. 保持当前的健康数据记录习惯
2. 关注关键指标的变化趋势
3. 结合生活实际理解数据意义

### 下一步行动建议：
1. 定期回顾分析结果（建议每周一次）
2. 如有异常变化，及时关注
3. 将数据分析与日常生活结合

---

### ⚠️ 重要安全声明
**本分析仅为基于数据的模式描述，不构成医疗建议。**
**任何健康决策请咨询专业医生。**
**紧急医疗情况请立即联系医疗机构。**

---
报告生成: 健康数据分析脚本 v1.0
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report_path

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 健康数据分析脚本")
    print("=" * 60)
    
    # 设置文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/raw/health.csv"
    
    print(f"📁 分析文件: {file_path}")
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 加载数据
        df = load_health_data(file_path)
        if df is None:
            return
        
        # 2. 计算睡眠时长
        df = calculate_sleep_duration(df)
        
        # 3. 统计分析
        stats = analyze_basic_stats(df)
        
        # 4. 创建图表
        charts = create_basic_charts(df)
        
        # 5. 生成报告
        report_path = generate_report(stats, charts, file_path)
        
        print(f"\n" + "=" * 60)
        print(f"🎉 分析完成！")
        print(f"\n📋 生成的文件:")
        print(f"   报告文件: {report_path}")
        if charts:
            print(f"   图表文件: {len(charts)}个")
            for chart in charts:
                print(f"     • {os.path.basename(chart)}")
        
        print(f"\n💡 使用建议:")
        print(f"   1. 查看生成的报告和图表")
        print(f"   2. 基于分析结果调整生活习惯")
        print(f"   3. 定期运行本脚本更新分析")
        
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()