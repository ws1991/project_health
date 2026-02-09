# test_detection_rules.py
from constitution.parser.constitution_parser import ConstitutionParser
from constitution.rules.rule_evaluator import RuleEvaluator

# 加载宪法
parser = ConstitutionParser()
config = parser.load_from_file("constitution/data/constitution_structured.yaml")

# 创建规则评估器
evaluator = RuleEvaluator()

# 测试文本
test_cases = [
    ("专业文本包含数据", "数据显示这个趋势很明显，概率为80%"),
    ("医疗建议文本", "我建议你立即就医，你应该服用这个药物"),
    ("隐私信息文本", "我的姓名是张三，身份证号是123456"),
    ("中性文本", "今天天气不错，我们去散步吧")
]

print(" 检测规则系统测试\n")

for test_name, test_text in test_cases:
    print(f"\n 测试: {test_name}")
    print(f"文本: {test_text}")
    print("-" * 50)
    
    # 评估所有条款
    results = evaluator.batch_evaluate(config.clauses, test_text, "pre_check")
    
    for clause_id, result in results.items():
        clause = parser.get_clause_by_id(clause_id)
        status = " 通过" if result.overall_passed else " 失败"
        print(f"  {clause.name}: {status}")
        
        if not result.overall_passed and result.details:
            for detail in result.details:
                if not detail.passed:
                    print(f"    - 规则失败: {detail.message}")
    
    # 获取高风险条款
    high_risk = evaluator.get_high_risk_clauses(results)
    if high_risk:
        print(f"   高风险: {', '.join([cid for cid, _ in high_risk])}")

print("\n" + "=" * 50)
print(" 检测规则系统测试完成！")
