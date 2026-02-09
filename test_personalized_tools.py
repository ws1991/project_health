# test_personalized_tools.py
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from agent.tools import (
    personalized_health_analyzer,
    csv_data_validator,
    generate_health_report,
    ConstitutionalToolSelector
)

# 您的CSV数据
test_data = """index,date,exercise,getup,note,seizureScale,sleep,step,study
0,2026年1月28日,1,2026年1月28日 9:30 (GMT+8),轻微噩梦,1,2026年1月27日 23:00 (GMT+8),599,2
1,2026年1月29日,0,2026年1月29日 8:45 (GMT+8),无异常,0,2026年1月28日 22:30 (GMT+8),845,3
2,2026年1月30日,1,2026年1月30日 9:15 (GMT+8),睡眠良好,1,2026年1月29日 23:15 (GMT+8),720,1
3,2026年1月31日,1,2026年1月31日 8:30 (GMT+8),轻微头痛,0,2026年1月30日 22:45 (GMT+8),1024,2
4,2026年2月1日,0,2026年2月1日 9:00 (GMT+8),状态良好,1,2026年1月31日 23:30 (GMT+8),890,3"""

print(" 个性化健康数据分析工具测试")
print("=" * 70)

# 1. 数据验证
print("\n 步骤1: 数据验证")
validation = csv_data_validator(test_data)
if validation["success"]:
    print(" 数据验证通过")
    overview = validation["验证结果"]["基本验证"]
    print(f"  数据形状: {overview['行数']}行  {overview['列数']}列")
    print(f"  列名: {', '.join(overview['列名'])}")
    
    # 显示数据质量
    print("\n 数据质量检查:")
    for col, quality in validation["验证结果"]["数据质量"].items():
        print(f"  {col}: {quality['空值比例']} 空值, {quality['唯一值数量']} 唯一值")
else:
    print(f" 数据验证失败: {validation.get('error', '未知错误')}")

# 2. 个性化分析
print("\n 步骤2: 个性化健康分析")
analysis = personalized_health_analyzer(test_data)
if analysis["success"]:
    print(" 分析完成")
    
    # 显示数据概况
    overview = analysis["数据概况"]
    print(f"  数据规模: {overview['行数']}行  {overview['列数']}列")
    
    # 显示关键指标
    key_metrics = analysis["详细分析"]["关键指标分析"]
    print("\n 关键指标:")
    for metric, values in key_metrics.items():
        if metric == "步数":
            print(f"   {metric}:")
            for key, value in values.items():
                print(f"    {key}: {value}")
        elif metric == "癫痫量表":
            print(f"    {metric} (医疗数据，仅摘要):")
            for key, value in values.items():
                print(f"    {key}: {value}")
    
    # 显示模式识别
    patterns = analysis["详细分析"]["模式识别"]
    if patterns:
        print("\n 识别模式:")
        for pattern in patterns:
            print(f"   {pattern}")
    
    # 显示宪法遵循
    print("\n 宪法遵循:")
    for clause, desc in analysis["宪法遵循"].items():
        print(f"  {clause}: {desc}")
    
    # 显示安全声明
    print("\n 重要声明:")
    for statement in analysis["重要声明"]:
        print(f"  {statement}")
else:
    print(f" 分析失败: {analysis.get('error', '未知错误')}")

# 3. 生成报告
print("\n 步骤3: 生成宪法遵循报告")
report = generate_health_report(test_data, "compliance")
if report["success"]:
    print(" 报告生成完成")
    
    report_info = report["报告"]["报告信息"]
    print(f"\n 报告信息:")
    print(f"  标题: {report_info['标题']}")
    print(f"  生成时间: {report_info['生成时间']}")
    print(f"  报告类型: {report_info['报告类型']}")
    
    # 显示宪法检查结果
    if "宪法检查" in report["报告"]["章节"]:
        print("\n 宪法检查结果:")
        for check, result in report["报告"]["章节"]["宪法检查"].items():
            print(f"  {check}: {result}")

# 4. 测试工具选择器
print("\n 步骤4: 测试工具选择器")
selector = ConstitutionalToolSelector()

test_queries = [
    "分析我的健康数据",
    "验证CSV数据质量",
    "生成健康趋势报告",
    "保护我的隐私数据"
]

for query in test_queries:
    tools = selector.select_tools_for_query(query)
    print(f"   '{query}'  推荐工具: {tools}")

print("\n" + "=" * 70)
print(" 个性化工具测试完成！")
print("\n 系统能力总结:")
print("    特定CSV格式分析: 支持您的健康数据格式")
print("    宪法约束: 确保分析安全合规")
print("    隐私保护: 自动匿名化敏感信息")
print("    专业严谨: 基于数据的科学分析")
print("    工具智能选择: 根据查询推荐最佳工具")
