"""
健康数据分析工具 - 完整修正版
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool, StructuredTool


class HealthDataTools:
    """健康数据分析工具集"""
    
    @staticmethod
    def load_health_data(file_path: str) -> pd.DataFrame:
        """加载健康数据文件"""
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8')
            
            print(f"📊 数据加载成功: {len(df)} 行, {len(df.columns)} 列")
            print(f"   列名: {list(df.columns)}")
            
            # 标准化列名（小写，去除空格）
            df.columns = [col.strip().lower() for col in df.columns]
            
            # 解析日期列
            if 'date' in df.columns:
                try:
                    df['date_parsed'] = pd.to_datetime(
                        df['date'], 
                        format='%Y年%m月%d日',
                        errors='coerce'
                    )
                except:
                    df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            
            # 计算睡眠时长（如果有sleep和getup）
            if 'sleep' in df.columns and 'getup' in df.columns:
                df = HealthDataTools._calculate_sleep_duration(df)
            
            # 计算衍生指标
            df = HealthDataTools._calculate_derived_metrics(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"数据加载失败: {str(e)}")
    
    @staticmethod
    def _calculate_sleep_duration(df: pd.DataFrame) -> pd.DataFrame:
        """计算睡眠时长"""
        def parse_time(time_str):
            """解析时间字符串"""
            try:
                if pd.isna(time_str):
                    return pd.NaT
                
                time_str = str(time_str)
                if '(' in time_str:
                    time_part = time_str.split('(')[0].strip()
                else:
                    time_part = time_str
                
                for fmt in ['%Y年%m月%d日 %H:%M', '%Y年%m月%d日']:
                    try:
                        return datetime.strptime(time_part, fmt)
                    except:
                        continue
                
                return pd.NaT
            except:
                return pd.NaT
        
        # 解析时间
        df['sleep_time'] = df['sleep'].apply(parse_time)
        df['getup_time'] = df['getup'].apply(parse_time)
        
        # 计算睡眠时长（小时）
        mask = df['sleep_time'].notna() & df['getup_time'].notna()
        df.loc[mask, 'sleep_duration_hours'] = (
            (df.loc[mask, 'getup_time'] - df.loc[mask, 'sleep_time']).dt.total_seconds() / 3600
        )
        
        # 调整跨天睡眠
        df.loc[df['sleep_duration_hours'] < 0, 'sleep_duration_hours'] += 24
        
        return df
    
    @staticmethod
    def _calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """计算衍生指标"""
        # 1. 发作程度分类
        if 'seizurescale' in df.columns:
            conditions = [
                df['seizurescale'] == 0,
                df['seizurescale'] == 1,
                df['seizurescale'] >= 2
            ]
            choices = ['无发作', '轻度发作', '中度以上发作']
            df['seizure_category'] = np.select(conditions, choices, default='未知')
        
        # 2. 步数等级
        if 'step' in df.columns:
            conditions = [
                df['step'] < 5000,
                (df['step'] >= 5000) & (df['step'] < 8000),
                (df['step'] >= 8000) & (df['step'] < 10000),
                df['step'] >= 10000
            ]
            choices = ['低活动量', '中等活动量', '高活动量', '极高活动量']
            df['step_level'] = np.select(conditions, choices, default='未知')
        
        # 3. 学习强度分类
        if 'study' in df.columns:
            conditions = [
                df['study'] == 0,
                df['study'] == 1,
                df['study'] == 2,
                df['study'] >= 3
            ]
            choices = ['无学习', '轻度学习', '中度学习', '高强度学习']
            df['study_intensity'] = np.select(conditions, choices, default='未知')
        
        # 4. 运动频率（滚动平均）
        if 'exercise' in df.columns and 'date_parsed' in df.columns:
            df = df.sort_values('date_parsed')
            df['exercise_7day_avg'] = df['exercise'].rolling(window=7, min_periods=1).mean()
        
        return df
    
    @staticmethod
    def analyze_basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """分析基本统计量"""
        analysis = {
            "数据概览": {},
            "数值列统计": {},
            "分类列分布": {},
            "时间范围": {},
            "数据质量": {}
        }
        
        # 数据概览
        analysis["数据概览"] = {
            "总记录数": len(df),
            "总列数": len(df.columns),
            "数据列": list(df.columns)
        }
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            analysis["数值列统计"][col] = {
                "count": int(df[col].count()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "25%": float(df[col].quantile(0.25)),
                "median": float(df[col].median()),
                "75%": float(df[col].quantile(0.75)),
                "max": float(df[col].max()),
                "missing": int(df[col].isnull().sum())
            }
        
        # 分类列分布
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:5]:
            if df[col].notna().any():
                value_counts = df[col].value_counts().head(5).to_dict()
                analysis["分类列分布"][col] = {
                    "unique_values": int(df[col].nunique()),
                    "top_values": value_counts
                }
        
        # 时间范围
        if 'date_parsed' in df.columns and df['date_parsed'].notna().any():
            analysis["时间范围"] = {
                "start": df['date_parsed'].min().strftime('%Y-%m-%d'),
                "end": df['date_parsed'].max().strftime('%Y-%m-%d'),
                "days": (df['date_parsed'].max() - df['date_parsed'].min()).days
            }
        
        # 数据质量
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        analysis["数据质量"] = {
            "完整性": f"{(1 - missing_cells / total_cells) * 100:.1f}%",
            "缺失值总数": int(missing_cells),
            "完全记录数": int((~df.isnull().any(axis=1)).sum())
        }
        
        return analysis
    
    @staticmethod
    def generate_basic_charts(df: pd.DataFrame, save_dir: str = "output/figures") -> Dict[str, str]:
        """生成基本图表"""
        import matplotlib.pyplot as plt
        import os
        
        os.makedirs(save_dir, exist_ok=True)
        charts = {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. 发作程度分布图
            if 'seizurescale' in df.columns:
                plt.figure(figsize=(10, 6))
                seizure_counts = df['seizurescale'].value_counts().sort_index()
                colors = ['green' if x == 0 else 'orange' if x == 1 else 'red' for x in seizure_counts.index]
                plt.bar([str(x) for x in seizure_counts.index], seizure_counts.values, color=colors, alpha=0.7)
                plt.title('发作程度分布', fontsize=14)
                plt.xlabel('发作程度 (0=无, 1=轻度, ≥2=中度以上)')
                plt.ylabel('天数')
                plt.grid(True, alpha=0.3)
                
                chart_path = f"{save_dir}/seizure_distribution_{timestamp}.png"
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()
                charts['seizure_distribution'] = chart_path
        except Exception as e:
            print(f"图表1生成失败: {e}")
        
        try:
            # 2. 睡眠时长分布
            if 'sleep_duration_hours' in df.columns:
                plt.figure(figsize=(10, 6))
                sleep_data = df['sleep_duration_hours'].dropna()
                if len(sleep_data) > 0:
                    plt.hist(sleep_data, bins=15, color='blue', alpha=0.7, edgecolor='black')
                    plt.axvline(x=7, color='red', linestyle='--', linewidth=2, label='推荐值(7h)')
                    plt.axvline(x=sleep_data.mean(), color='green', linestyle='-', linewidth=2, label=f'均值({sleep_data.mean():.1f}h)')
                    plt.title('睡眠时长分布', fontsize=14)
                    plt.xlabel('睡眠时长(小时)')
                    plt.ylabel('频次')
                    plt.legend()
                    plt.grid(True, alpha=0.3)
                    
                    chart_path = f"{save_dir}/sleep_distribution_{timestamp}.png"
                    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    charts['sleep_distribution'] = chart_path
        except Exception as e:
            print(f"图表2生成失败: {e}")
        
        try:
            # 3. 步数趋势图
            if 'step' in df.columns:
                plt.figure(figsize=(12, 6))
                df_sorted = df.sort_values('date_parsed') if 'date_parsed' in df.columns else df
                plt.plot(range(len(df_sorted)), df_sorted['step'], marker='o', linewidth=2, color='green')
                plt.axhline(y=10000, color='red', linestyle='--', linewidth=1, label='目标(10000)')
                plt.axhline(y=5000, color='orange', linestyle='--', linewidth=1, label='最低(5000)')
                plt.title('每日步数趋势', fontsize=14)
                plt.xlabel('记录序号')
                plt.ylabel('步数')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                chart_path = f"{save_dir}/step_trend_{timestamp}.png"
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()
                charts['step_trend'] = chart_path
        except Exception as e:
            print(f"图表3生成失败: {e}")
        
        return charts
    
    @staticmethod
    def analyze_seizure_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        """分析发作模式"""
        analysis = {
            "发作概况": {},
            "时间模式": {},
            "关联分析": {},
            "备注分析": {}
        }
        
        if 'seizurescale' not in df.columns:
            return {"error": "数据中未找到发作程度列 (seizureScale)"}
        
        # 发作概况
        seizure_data = df['seizurescale'].dropna()
        total_days = len(seizure_data)
        
        if total_days == 0:
            return {"error": "发作程度数据全为空"}
        
        seizure_days = len(seizure_data[seizure_data > 0])
        
        analysis["发作概况"] = {
            "总天数": total_days,
            "发作天数": seizure_days,
            "发作频率": f"{(seizure_days / total_days * 100):.1f}%" if total_days > 0 else "0%",
            "平均发作程度": float(seizure_data.mean()),
            "最大发作程度": int(seizure_data.max())
        }
        
        # 发作程度分布
        severity_counts = seizure_data.value_counts().sort_index()
        severity_dist = {}
        for severity, count in severity_counts.items():
            percentage = (count / total_days * 100) if total_days > 0 else 0
            description = {
                0: "无发作",
                1: "轻度发作",
                2: "中度发作",
                3: "严重发作"
            }.get(severity, f"程度{severity}")
            severity_dist[description] = {
                "天数": int(count),
                "占比": f"{percentage:.1f}%"
            }
        analysis["发作概况"]["严重程度分布"] = severity_dist
        
        # 关联分析
        if 'sleep_duration_hours' in df.columns:
            seizure_by_sleep = df.groupby('seizurescale')['sleep_duration_hours'].mean()
            analysis["关联分析"]["发作与睡眠平均时长"] = seizure_by_sleep.to_dict()
        
        if 'step' in df.columns:
            seizure_by_steps = df.groupby('seizurescale')['step'].mean()
            analysis["关联分析"]["发作与平均步数"] = seizure_by_steps.to_dict()
        
        if 'study' in df.columns:
            seizure_by_study = df.groupby('seizurescale')['study'].mean()
            analysis["关联分析"]["发作与学习强度"] = seizure_by_study.to_dict()
        
        # 备注分析
        if 'note' in df.columns:
            seizure_notes = df[df['seizurescale'] > 0]['note'].dropna()
            if len(seizure_notes) > 0:
                keywords = ['噩梦', '压力', '疲劳', '紧张', '头痛', '失眠', '饮酒', '熬夜']
                keyword_counts = {}
                for kw in keywords:
                    count = sum(1 for note in seizure_notes if kw in str(note))
                    if count > 0:
                        keyword_counts[kw] = count
                
                analysis["备注分析"] = {
                    "发作日备注数量": len(seizure_notes),
                    "高频关键词": keyword_counts,
                    "样本备注": seizure_notes.head(3).tolist() if len(seizure_notes) > 0 else []
                }
        
        return analysis


# ================= LangChain工具封装 =================
def get_all_tools() -> List[BaseTool]:
    """获取所有可用工具"""
    
    def load_health_data_tool(file_path: str) -> str:
        """加载健康数据文件"""
        try:
            df = HealthDataTools.load_health_data(file_path)
            date_info = ""
            if 'date_parsed' in df.columns and df['date_parsed'].notna().any():
                date_info = f"{df['date_parsed'].min().strftime('%Y-%m-%d')} 至 {df['date_parsed'].max().strftime('%Y-%m-%d')}"
            
            return f"""
✅ 数据加载成功
- 文件: {file_path}
- 记录数: {len(df)} 行
- 列数: {len(df.columns)} 列
- 主要列: {list(df.columns)[:8]}
- 时间范围: {date_info if date_info else '未知'}

📊 数据已就绪，可以进行下一步分析。
"""
        except Exception as e:
            return f"❌ 数据加载失败: {str(e)}"
    
    def analyze_stats_tool(file_path: str) -> str:
        """分析健康数据统计量"""
        try:
            df = HealthDataTools.load_health_data(file_path)
            analysis = HealthDataTools.analyze_basic_stats(df)
            
            output = "📈 健康数据统计分析\n"
            output += "=" * 50 + "\n"
            
            output += "\n📊 数据概览:\n"
            for key, value in analysis["数据概览"].items():
                output += f"  {key}: {value}\n"
            
            output += "\n📊 关键指标统计:\n"
            for col in ['seizurescale', 'step', 'study']:
                if col in analysis["数值列统计"]:
                    stats = analysis["数值列统计"][col]
                    output += f"  {col}:\n"
                    output += f"    平均值: {stats['mean']:.2f}\n"
                    output += f"    范围: {stats['min']} - {stats['max']}\n"
            
            if 'sleep_duration_hours' in df.columns:
                sleep_stats = df['sleep_duration_hours'].describe()
                output += f"  睡眠时长:\n"
                output += f"    平均值: {sleep_stats['mean']:.1f}小时\n"
                output += f"    范围: {sleep_stats['min']:.1f} - {sleep_stats['max']:.1f}小时\n"
            
            output += "\n🔍 数据质量:\n"
            for key, value in analysis["数据质量"].items():
                output += f"  {key}: {value}\n"
            
            return output
            
        except Exception as e:
            return f"❌ 统计分析失败: {str(e)}"
    
    def generate_charts_tool(file_path: str) -> str:
        """生成健康数据图表"""
        try:
            df = HealthDataTools.load_health_data(file_path)
            charts = HealthDataTools.generate_basic_charts(df)
            
            if not charts:
                return "⚠️  未能生成图表，请检查数据列"
            
            output = "📊 图表生成完成\n"
            output += "=" * 50 + "\n"
            
            for chart_name, chart_path in charts.items():
                output += f"✅ {chart_name.replace('_', ' ').title()}\n"
                output += f"   文件: {chart_path}\n"
            
            output += "\n💡 图表已保存到 output/figures/ 目录"
            return output
            
        except Exception as e:
            return f"❌ 图表生成失败: {str(e)}"
    
    def analyze_seizure_tool(file_path: str) -> str:
        """分析发作模式"""
        try:
            df = HealthDataTools.load_health_data(file_path)
            analysis = HealthDataTools.analyze_seizure_patterns(df)
            
            if "error" in analysis:
                return f"❌ {analysis['error']}"
            
            output = "🔍 发作模式分析报告\n"
            output += "=" * 50 + "\n"
            
            output += "\n📊 发作概况:\n"
            for key, value in analysis["发作概况"].items():
                if key == "严重程度分布":
                    output += f"  {key}:\n"
                    for desc, stats in value.items():
                        output += f"    {desc}: {stats['天数']}天 ({stats['占比']})\n"
                else:
                    output += f"  {key}: {value}\n"
            
            if "备注分析" in analysis and analysis["备注分析"]:
                output += "\n📝 备注关键词分析:\n"
                keywords = analysis["备注分析"].get("高频关键词", {})
                if keywords:
                    for kw, count in keywords.items():
                        output += f"    {kw}: {count}次\n"
                else:
                    output += "    未发现高频关键词\n"
            
            output += "\n⚠️  **重要声明**: 本分析仅为数据模式描述，不构成医疗建议。"
            output += "\n    任何健康决策请咨询专业医生。"
            
            return output
            
        except Exception as e:
            return f"❌ 发作模式分析失败: {str(e)}"
    
    def generate_constitutional_report_tool(file_path: str) -> str:
        """按照宪法要求的格式生成分析报告"""
        try:
            # 导入需要的模块
            import os
            from datetime import datetime
            
            # 1. 准备数据和分析
            df = HealthDataTools.load_health_data(file_path)
            stats = HealthDataTools.analyze_basic_stats(df)
            seizure_analysis = HealthDataTools.analyze_seizure_patterns(df)
            charts = HealthDataTools.generate_basic_charts(df)
            
            # 2. 创建报告目录
            report_dir = "output/reports"
            os.makedirs(report_dir, exist_ok=True)
            
            # 3. 生成报告路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"{report_dir}/constitutional_report_{timestamp}.md"
            
            # 4. 构建报告内容
            report = f"""# 健康数据分析报告（宪法格式）

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**数据文件**: {file_path}
**分析天数**: {stats["数据概览"]["总记录数"]}

## 【核心结论】
"""
            
            # 生成核心结论
            conclusions = []
            
            if "error" not in seizure_analysis:
                seizure_freq = seizure_analysis['发作概况']['发作频率']
                avg_severity = seizure_analysis['发作概况']['平均发作程度']
                severity_desc = "轻微" if avg_severity < 1 else "中等" if avg_severity < 2 else "较重"
                conclusions.append(f"发作频率 {seizure_freq}，平均程度 {avg_severity:.2f}（{severity_desc}）")
            
            if 'sleep_duration_hours' in df.columns:
                avg_sleep = df['sleep_duration_hours'].mean()
                sleep_status = "良好" if 7 <= avg_sleep <= 9 else "偏短" if avg_sleep < 7 else "偏长"
                conclusions.append(f"平均睡眠时长 {avg_sleep:.1f}小时（{sleep_status}）")
            
            if 'step' in df.columns:
                avg_steps = df['step'].mean()
                activity_level = "充足" if avg_steps >= 8000 else "中等" if avg_steps >= 5000 else "不足"
                conclusions.append(f"日均步数 {int(avg_steps)}步（活动量{activity_level}）")
            
            if 'study' in df.columns:
                avg_study = df['study'].mean()
                study_level = "较低" if avg_study < 1 else "适中" if avg_study < 2 else "较高"
                conclusions.append(f"平均学习强度 {avg_study:.1f}（{study_level}）")
            
            # 写入核心结论
            for i, conclusion in enumerate(conclusions, 1):
                report += f"{i}. {conclusion}\n"
            
            report += """
## 【支持数据/代码】

### 1. 关键数据统计
"""
            
            # 添加关键数据
            if "error" not in seizure_analysis:
                report += f"- **发作数据**:\n"
                report += f"  - 总天数: {seizure_analysis['发作概况']['总天数']}\n"
                report += f"  - 发作天数: {seizure_analysis['发作概况']['发作天数']}\n"
                report += f"  - 发作频率: {seizure_analysis['发作概况']['发作频率']}\n"
                report += f"  - 平均程度: {seizure_analysis['发作概况']['平均发作程度']:.2f}\n"
            
            report += f"- **睡眠数据**:\n"
            if 'sleep_duration_hours' in df.columns:
                sleep_data = df['sleep_duration_hours'].dropna()
                if len(sleep_data) > 0:
                    report += f"  - 平均值: {sleep_data.mean():.1f}小时\n"
                    report += f"  - 最小值: {sleep_data.min():.1f}小时\n"
                    report += f"  - 最大值: {sleep_data.max():.1f}小时\n"
                    report += f"  - 标准差: {sleep_data.std():.1f}小时\n"
            
            report += f"- **活动数据**:\n"
            if 'step' in df.columns:
                step_data = df['step'].dropna()
                if len(step_data) > 0:
                    report += f"  - 平均值: {int(step_data.mean())}步\n"
                    report += f"  - 最小值: {int(step_data.min())}步\n"
                    report += f"  - 最大值: {int(step_data.max())}步\n"
                    report += f"  - 标准差: {int(step_data.std())}步\n"
            
            # 添加图表信息
            if charts:
                report += "\n### 2. 生成的可视化图表\n"
                for chart_name, chart_path in charts.items():
                    chart_desc = chart_name.replace('_', ' ').title()
                    report += f"- {chart_desc}: 已保存至 `{chart_path}`\n"
            
            # 添加代码示例
            report += """
### 3. 核心分析代码示例
```python
# 数据加载与预处理
import pandas as pd
import numpy as np

def load_and_preprocess(file_path):
    \"\"\"加载并预处理健康数据\"\"\"
    df = pd.read_csv(file_path, encoding='utf-8')
    df.columns = [col.strip().lower() for col in df.columns]
    
    # 解析日期
    if 'date' in df.columns:
        df['date_parsed'] = pd.to_datetime(df['date'], format='%Y年%m月%d日', errors='coerce')
    
    # 计算睡眠时长
    def parse_time(time_str):
        if pd.isna(time_str):
            return pd.NaT
        time_str = str(time_str)
        if '(' in time_str:
            time_part = time_str.split('(')[0].strip()
        else:
            time_part = time_str
        
        for fmt in ['%Y年%m月%d日 %H:%M', '%Y年%m月%d日']:
            try:
                return pd.datetime.strptime(time_part, fmt)
            except:
                continue
        return pd.NaT
    
    if 'sleep' in df.columns and 'getup' in df.columns:
        df['sleep_time'] = df['sleep'].apply(parse_time)
        df['getup_time'] = df['getup'].apply(parse_time)
        mask = df['sleep_time'].notna() & df['getup_time'].notna()
        df.loc[mask, 'sleep_duration_hours'] = (
            (df.loc[mask, 'getup_time'] - df.loc[mask, 'sleep_time']).dt.total_seconds() / 3600
        )
    
    return df

# 基本统计分析
def basic_analysis(df):
    \"\"\"基础统计分析\"\"\"
    results = {}
    
    if 'seizurescale' in df.columns:
        seizure_data = df['seizurescale'].dropna()
        results['seizure'] = {
            'mean': float(seizure_data.mean()),
            'frequency': f"{(seizure_data > 0).mean() * 100:.1f}%",
            'max': int(seizure_data.max())
        }
    
    if 'sleep_duration_hours' in df.columns:
        sleep_data = df['sleep_duration_hours'].dropna()
        results['sleep'] = {
            'mean': float(sleep_data.mean()),
            'min': float(sleep_data.min()),
            'max': float(sleep_data.max())
        }
    
    if 'step' in df.columns:
        step_data = df['step'].dropna()
        results['step'] = {
            'mean': float(step_data.mean()),
            'min': float(step_data.min()),
            'max': float(step_data.max())
        }
    
    return results
```
    report += """
        # ✅ 5. 保存报告到文件（正确位置：return之前）
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

            # ✅ 6. 返回给用户的成功消息（正确位置：最后）
            return f"""✅ 健康数据分析报告已生成"""
        except Exception as e:
            return f"❌ 宪法格式报告生成失败: {str(e)}"

    # 创建工具列表
    tools = [
        StructuredTool.from_function(
            func=load_health_data_tool,
            name="load_health_data",
            description="加载健康数据CSV文件"
        ),
        StructuredTool.from_function(
            func=analyze_stats_tool,
            name="analyze_health_stats",
            description="分析健康数据的基本统计量"
        ),
        StructuredTool.from_function(
            func=generate_charts_tool,
            name="generate_health_charts",
            description="生成健康数据可视化图表"
        ),
        StructuredTool.from_function(
            func=analyze_seizure_tool,
            name="analyze_seizure_patterns",
            description="专项分析发作模式"
        ),
        StructuredTool.from_function(
            func=generate_constitutional_report_tool,
            name="generate_constitutional_report",
            description="按照宪法格式生成健康分析报告，包含核心结论、支持数据、下一步建议三部分"
        ),
    ]

    return tools