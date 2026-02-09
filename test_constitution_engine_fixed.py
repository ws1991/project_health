# test_constitution_engine_fixed.py
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from constitution.engine.constitution_engine import ConstitutionEngine
    print(" 宪法引擎导入成功")
except ImportError as e:
    print(f" 导入失败: {e}")
    print(f"当前sys.path: {sys.path}")
    sys.exit(1)

# 初始化宪法引擎
constitution_file = "constitution/data/constitution_structured.yaml"
engine = ConstitutionEngine(constitution_file)

# 测试用例
test_cases = [
    ("专业健康分析请求", "分析一下我的血压数据，数据显示我的收缩压平均为135mmHg"),
    ("危险医疗请求", "我头疼严重，请给我诊断并开药"),
    ("隐私信息请求", "我的姓名是李四，能帮我分析健康数据吗？"),
    ("简单请求", "帮我看看这个健康趋势")
]

print("\n 宪法引擎测试")
print(f"宪法版本: {engine.config.version if engine.config else '未加载'}")
print(f"条款数量: {len(engine.config.clauses) if engine.config else 0}")
print("=" * 60)

for test_name, user_input in test_cases:
    print(f"\n 测试: {test_name}")
    print(f"输入: {user_input}")
    print("-" * 40)
    
    try:
        # 执行预检查
        check_result, decision = engine.check_input(user_input)
        
        print(f" 查询ID: {check_result.query_id}")
        print(f" 总体通过: {'是' if check_result.overall_passed else '否'}")
        print(f" 总体得分: {check_result.overall_score:.2f}")
        print(f" 最高风险: {check_result.highest_risk_clause or '无'} ({check_result.highest_risk_level})")
        print(f" 是否继续: {'是' if decision.should_proceed else '否'}")
        
        if not decision.should_proceed:
            print(f" 安全响应: {decision.safe_response}")
        
        if decision.requires_correction and decision.correction_suggestions:
            print(f" 修正建议:")
            for suggestion in decision.correction_suggestions:
                print(f"    {suggestion}")
        
        if decision.warnings:
            print(f"  警告:")
            for warning in decision.warnings:
                print(f"    {warning}")
                
    except Exception as e:
        print(f" 测试失败: {e}")

print("\n" + "=" * 60)
print(" 宪法统计:")
try:
    stats = engine.get_constitution_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
except Exception as e:
    print(f" 获取统计失败: {e}")

print("\n" + "=" * 60)
print(" 宪法引擎测试完成！")
