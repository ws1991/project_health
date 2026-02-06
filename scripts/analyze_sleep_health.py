#!/usr/bin/env python3
"""
睡眠健康数据分析主脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

from src.data.loader import EnhancedDataLoader
from src.features.time_features import TimeFeatureEngineer
from src.features.health_features import HealthFeatureEngineer
from src.analysis.sleep_analysis import SleepAnalyzer
from src.analysis.seizure_analysis import SeizureAnalyzer
from src.visualization.plots import HealthDataVisualizer

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SleepHealthAnalysisPipeline:
    """睡眠健康数据分析流水线"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.df = None
        self.df_features = None
        self.results = {}
        
    def run(self, data_path: str, output_dir: str = "output"):
        """运行完整分析流水线"""
        logger.info("开始睡眠健康数据分析流水线")
        
        # 1. 创建输出目录
        self._create_output_dir(output_dir)
        
        # 2. 加载和预处理数据
        self.load_and_preprocess(data_path)
        
        # 3. 特征工程
        self.create_features()
        
        # 4. 分析
        self.perform_analysis()
        
        # 5. 可视化
        self.create_visualizations(output_dir)
        
        # 6. 生成报告
        self.generate_report(output_dir)
        
        logger.info("分析流水线完成")
        
    def _create_output_dir(self, output_dir: str):
        """创建输出目录"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(f"{output_dir}/figures").mkdir(parents=True, exist_ok=True)
        Path(f"{output_dir}/tables").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
    
    def load_and_preprocess(self, data_path: str):
        """加载和预处理数据"""
        logger.info("加载和预处理数据...")
        
        # 加载数据
        loader = EnhancedDataLoader(self.config_path)
        self.df = loader.load_and_parse_data(data_path)
        
        # 保存处理后的数据
        self.df.to_csv("output/processed_data.csv", index=False, encoding='utf-8')
        
        logger.info(f"数据加载完成，形状: {self.df.shape}")
        logger.info(f"数据列: {list(self.df.columns)}")
        
        # 显示数据摘要
        self._show_data_summary()
    
    def _show_data_summary(self):
        """显示数据摘要"""
        print("\n" + "="*60)
        print("数据摘要")
        print("="*60)
        
        print(f"数据期间: {self.df['date'].min().date()} 到 {self.df['date'].max().date()}")
        print(f"总天数: {len(self.df)}")
        
        if 'seizure' in self.df.columns:
            seizure_days = (self.df['seizure'] > 0).sum()
            print(f"有发作天数: {seizure_days} ({seizure_days/len(self.df)*100:.1f}%)")
        
        if 'sleep_duration_hours' in self.df.columns:
            avg_sleep = self.df['sleep_duration_hours'].mean()
            print(f"平均睡眠时长: {avg_sleep:.1f}小时")
        
        if 'step' in self.df.columns:
            avg_steps = self.df['step'].mean()
            print(f"平均步数: {avg_steps:.0f}")
        
        print("="*60 + "\n")
    
    def create_features(self):
        """执行特征工程"""
        logger.info("执行特征工程...")
        
        # 时间特征
        time_engineer = TimeFeatureEngineer()
        df_time_features = time_engineer.create_time_features(self.df)
        
        # 健康特征
        health_engineer = HealthFeatureEngineer()
        self.df_features = health_engineer.create_health_features(df_time_features)
        
        # 保存特征数据
        self.df_features.to_csv("output/features_data.csv", index=False, encoding='utf-8')
        
        logger.info(f"特征工程完成，特征数: {len(self.df_features.columns)}")
        logger.info(f"新增特征: {list(set(self.df_features.columns) - set(self.df.columns))}")
    
    def perform_analysis(self):
        """执行分析"""
        logger.info("执行数据分析...")
        
        # 睡眠分析
        sleep_analyzer = SleepAnalyzer()
        self.results['sleep'] = sleep_analyzer.analyze(self.df_features)
        
        # 癫痫分析
        seizure_analyzer = SeizureAnalyzer()
        self.results['seizure'] = seizure_analyzer.analyze(self.df_features)
        
        # 相关性分析
        correlation_results = self._analyze_correlations()
        self.results['correlations'] = correlation_results
        
        # 保存分析结果
        self._save_analysis_results()
    
    def _analyze_correlations(self) -> dict:
        """分析相关性"""
        logger.info("分析特征相关性...")
        
        # 选择数值列
        numeric_cols = self.df_features.select_dtypes(include=[np.number]).columns
        
        # 计算相关系数矩阵
        corr_matrix = self.df_features[numeric_cols].corr()
        
        # 找出与癫痫发作相关性最强的特征
        if 'seizure' in numeric_cols:
            seizure_correlations = corr_matrix['seizure'].sort_values(ascending=False)
            top_correlations = seizure_correlations.head(10)
        else:
            top_correlations = pd.Series()
        
        # 保存相关性矩阵
        corr_matrix.to_csv("output/tables/correlation_matrix.csv")
        
        return {
            'matrix': corr_matrix,
            'top_correlations': top_correlations,
            'numeric_features': list(numeric_cols)
        }
    
    def _save_analysis_results(self):
        """保存分析结果"""
        import json
        
        # 转换为可序列化的格式
        serializable_results = {}
        for category, results in self.results.items():
            if category == 'correlations':
                serializable_results[category] = {
                    'top_correlations': results['top_correlations'].to_dict()
                }
            else:
                serializable_results[category] = results
        
        # 保存为JSON
        with open('output/analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
    
    def create_visualizations(self, output_dir: str):
        """创建可视化图表"""
        logger.info("创建可视化图表...")
        
        visualizer = HealthDataVisualizer()
        
        # 1. 综合报告
        fig_comprehensive = visualizer.create_comprehensive_report(
            self.df_features, 
            self.results
        )
        visualizer.save_figure(fig_comprehensive, f"{output_dir}/figures/comprehensive_report.html")
        
        # 2. 睡眠分析图表
        fig_sleep = visualizer.create_sleep_analysis_plots(self.df_features)
        visualizer.save_figure(fig_sleep, f"{output_dir}/figures/sleep_analysis.png")
        
        # 3. 癫痫分析图表
        fig_seizure = visualizer.create_seizure_analysis_plots(self.df_features)
        visualizer.save_figure(fig_seizure, f"{output_dir}/figures/seizure_analysis.png")
        
        # 4. 相关性热图
        fig_corr = visualizer.create_correlation_heatmap(self.results['correlations']['matrix'])
        visualizer.save_figure(fig_corr, f"{output_dir}/figures/correlation_heatmap.png")
        
        logger.info("可视化图表创建完成")
    
    def generate_report(self, output_dir: str):
        """生成分析报告"""
        logger.info("生成分析报告...")
        
        report_content = self._create_report_content()
        
        # 保存为Markdown
        with open(f"{output_dir}/sleep_health_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存为HTML（可选）
        self._save_html_report(report_content, f"{output_dir}/report.html")
        
        logger.info(f"报告已保存至: {output_dir}/sleep_health_analysis_report.md")
    
    def _create_report_content(self) -> str:
        """创建报告内容"""
        content = []
        
        content.append("# 睡眠健康数据分析报告")
        content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # 数据概览
        content.append("## 1. 数据概览")
        content.append(f"- 分析期间: {self.df['date'].min().date()} 到 {self.df['date'].max().date()}")
        content.append(f"- 总天数: {len(self.df)}")
        
        if 'seizure' in self.df.columns:
            seizure_days = (self.df['seizure'] > 0).sum()
            content.append(f"- 有发作天数: {seizure_days} ({seizure_days/len(self.df)*100:.1f}%)")
        
        # 睡眠分析结果
        if 'sleep' in self.results:
            sleep_results = self.results['sleep']
            content.append("\n## 2. 睡眠分析")
            content.append(f"- 平均睡眠时长: {sleep_results.get('avg_sleep_duration', 'N/A'):.1f}小时")
            content.append(f"- 睡眠规律性评分: {sleep_results.get('regularity_score', 'N/A')}/10")
            
            if 'sleep_insights' in sleep_results:
                content.append("\n### 睡眠洞察:")
                for insight in sleep_results['sleep_insights']:
                    content.append(f"- {insight}")
        
        # 癫痫分析结果
        if 'seizure' in self.results:
            seizure_results = self.results['seizure']
            content.append("\n## 3. 癫痫发作分析")
            content.append(f"- 发作频率: {seizure_results.get('frequency', 'N/A')}次/天")
            content.append(f"- 平均发作强度: {seizure_results.get('avg_intensity', 'N/A'):.2f}")
            
            if 'trigger_factors' in seizure_results:
                content.append("\n### 可能的触发因素:")
                for factor, correlation in seizure_results['trigger_factors'].items():
                    content.append(f"- {factor}: {correlation:.3f}")
        
        # 相关性分析
        if 'correlations' in self.results:
            corr_results = self.results['correlations']
            content.append("\n## 4. 关键相关性")
            
            if 'top_correlations' in corr_results:
                top_corr = corr_results['top_correlations']
                content.append("### 与癫痫发作相关性最强的特征:")
                for feature, correlation in list(top_corr.items())[1:6]:  # 跳过自身相关性
                    content.append(f"- {feature}: {correlation:.3f}")
        
        # 建议
        content.append("\n## 5. 健康建议")
        content.extend(self._generate_recommendations())
        
        return "\n".join(content)
    
    def _generate_recommendations(self) -> list:
        """生成健康建议"""
        recommendations = []
        
        # 睡眠建议
        if 'sleep_duration_hours' in self.df.columns:
            avg_sleep = self.df['sleep_duration_hours'].mean()
            if avg_sleep < 7:
                recommendations.append("💤 **睡眠建议**: 您的平均睡眠时长不足7小时，建议增加睡眠时间，目标7-9小时")
            elif avg_sleep > 9:
                recommendations.append("💤 **睡眠建议**: 您的睡眠时长可能过多，建议保持7-9小时的睡眠")
            else:
                recommendations.append("💤 **睡眠建议**: 您的睡眠时长在理想范围内，继续保持")
        
        # 活动建议
        if 'step' in self.df.columns:
            avg_steps = self.df['step'].mean()
            if avg_steps < 5000:
                recommendations.append("🚶 **活动建议**: 每日平均步数低于5000步，建议增加日常活动量")
            elif avg_steps < 7500:
                recommendations.append("🚶 **活动建议**: 您的活动量适中，可以考虑增加到7500步以上")
            else:
                recommendations.append("🚶 **活动建议**: 您的活动量充足，继续保持")
        
        # 癫痫管理建议
        if 'seizure' in self.df.columns and (self.df['seizure'] > 0).any():
            recommendations.append("⚠️ **健康管理**: 监测到癫痫发作记录，请密切观察并与医生保持沟通")
            
            # 如果有相关性强的因素
            if 'correlations' in self.results:
                top_corr = self.results['correlations']['top_correlations']
                for feature, correlation in list(top_corr.items())[1:3]:
                    if abs(correlation) > 0.3:
                        direction = "增加" if correlation > 0 else "减少"
                        recommendations.append(f"📊 **观察项**: {feature} 与发作呈现{direction}相关")
        
        return recommendations
    
    def _save_html_report(self, markdown_content: str, output_path: str):
        """保存为HTML报告"""
        try:
            import markdown
            html_content = markdown.markdown(markdown_content)
            
            # 添加基本样式
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>睡眠健康分析报告</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                    h3 {{ color: #7f8c8d; }}
                    ul {{ padding-left: 20px; }}
                    li {{ margin: 8px 0; }}
                    .recommendation {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .insight {{ background-color: #e8f4fc; padding: 10px; margin: 5px 0; border-left: 4px solid #3498db; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
                
        except ImportError:
            logger.warning("markdown包未安装，跳过HTML报告生成")


def main():
    """主函数"""
    # 设置参数
    data_file = "data/sleep_health_data.csv"  # 你的数据文件路径
    output_dir = "analysis_results"
    
    # 创建并运行流水线
    pipeline = SleepHealthAnalysisPipeline()
    
    try:
        pipeline.run(data_file, output_dir)
        print("\n✅ 分析完成！")
        print(f"📁 结果保存在: {output_dir}/")
        print(f"📊 查看报告: {output_dir}/sleep_health_analysis_report.md")
        
    except Exception as e:
        logger.error(f"分析过程中出错: {e}", exc_info=True)
        print(f"\n❌ 分析失败: {e}")


if __name__ == "__main__":
    main()