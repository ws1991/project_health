# constitution/tests/trace_actual_flow.py
"""
基于您实际代码结构的宪法系统追踪
"""
import sys
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')

def trace_actual_constitution_flow():
    print("🔄 基于实际代码的宪法系统追踪")
    print("=" * 70)
    
    try:
        # 1. 导入您的实际模块
        print("\n1. 🔄 导入模块...")
        from constitution.parser.constitution_parser import ConstitutionParser
        from constitution.engine.constitution_engine import ConstitutionEngine, EnforcementDecision
        from constitution.rules.rule_evaluator import RuleEvaluator
        
        print("   ✅ 模块导入成功")
        print(f"   • ConstitutionParser: {ConstitutionParser}")
        print(f"   • ConstitutionEngine: {ConstitutionEngine}")
        print(f"   • RuleEvaluator: {RuleEvaluator}")
        
        # 2. 初始化引擎
        print("\n2. ⚙️ 初始化宪法引擎...")
        engine = ConstitutionEngine()
        
        # 查看引擎初始状态
        print(f"   • 引擎已创建: {engine}")
        print(f"   • Parser: {engine.parser}")
        print(f"   • Evaluator: {engine.evaluator}")
        print(f"   • Config: {engine.config}")
        
        # 3. 加载宪法文件
        print("\n3. 📥 加载宪法文件...")
        constitution_path = Path("constitution/data/constitution_structured.yaml")
        
        if constitution_path.exists():
            config = engine.load_constitution(str(constitution_path))
            print(f"   ✅ 宪法加载成功")
            print(f"   • 宪法版本: {config.version}")
            print(f"   • 条款数量: {len(config.clauses)}")
            print(f"   • 规则数量: {len(config.detection_rules)}")
            
            # 显示条款
            print(f"\n   📜 宪法条款:")
            for clause in config.clauses:
                print(f"     • {clause.id}: {clause.name}")
            
            # 显示规则类型统计
            print(f"\n   📊 检测规则统计:")
            rule_types = {}
            for rule in config.detection_rules:
                rule_type = rule.get('rule_type', 'unknown')
                rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
            
            for rule_type, count in rule_types.items():
                print(f"     • {rule_type}: {count}条")
        else:
            print(f"   ❌ 宪法文件不存在: {constitution_path}")
            return
        
        # 4. 测试检查流程
        print("\n4. 🧪 测试宪法检查流程...")
        
        test_cases = [
            ("简单查询", "显示我的健康数据"),
            ("医学建议", "我头痛需要吃什么药治疗？"),
            ("数据分析", "数据分析显示平均心率85次/分"),
            ("隐私信息", "张三的血压是120/80"),
        ]
        
        for case_name, query in test_cases:
            print(f"\n   🔍 测试: {case_name}")
            print(f"      查询: \"{query}\"")
            
            # 预检查
            pre_check = engine.check_input(query)
            print(f"      预检查: {'✅ 通过' if pre_check.passed else '❌ 违规'}")
            
            if not pre_check.passed and pre_check.violations:
                for violation in pre_check.violations:
                    print(f"        违规: {violation.get('rule_name', '未知')}")
            
            # 模拟工具输出
            tool_output = f"分析结果: 对于查询'{query}'，数据显示正常范围"
            
            # 后检查
            post_check = engine.check_output(tool_output, query)
            print(f"      后检查: {'✅ 通过' if post_check.passed else '❌ 需要修正'}")
            
            if post_check.correction_suggestions:
                for suggestion in post_check.correction_suggestions:
                    print(f"        修正建议: {suggestion}")
        
        # 5. 查看审计日志
        print("\n5. 📋 审计日志...")
        if engine.audit_logs:
            print(f"   日志数量: {len(engine.audit_logs)}")
            for i, log in enumerate(engine.audit_logs[-3:], 1):  # 显示最后3条
                print(f"   日志{i}: {log.get('action', '未知动作')}")
        else:
            print("   暂无审计日志")
        
        # 6. 查看决策过程
        print("\n6. 🎯 决策过程示例...")
        
        # 创建一个违规案例来查看决策
        risky_query = "请诊断我的病情并开处方药"
        print(f"   测试风险查询: \"{risky_query}\"")
        
        result = engine.check_input(risky_query)
        
        if not result.passed:
            print(f"   决策结果: 拒绝执行")
            if result.safe_response:
                print(f"   安全响应: {result.safe_response}")
        
        return engine
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print(f"当前Python路径: {sys.path}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()

def analyze_decision_making():
    """分析决策逻辑"""
    print("\n" + "=" * 70)
    print("🤔 决策逻辑分析")
    print("=" * 70)
    
    # 您的EnforcementDecision类分析
    print("\n📊 EnforcementDecision 类字段:")
    decision_fields = [
        ("should_proceed", "bool", "是否继续执行"),
        ("requires_correction", "bool", "是否需要修正"),
        ("correction_suggestions", "List[str]", "修正建议列表"),
        ("safe_response", "Optional[str]", "安全响应（拒绝时）"),
        ("warnings", "List[str]", "警告信息"),
        ("audit_info", "Dict[str, Any]", "审计信息")
    ]
    
    for field_name, field_type, description in decision_fields:
        print(f"   • {field_name}: {field_type} - {description}")
    
    print("\n💡 决策流程:")
    print("""
    1. 宪法引擎检查输入/输出
    2. 评估器执行所有规则检查
    3. 根据违规情况创建EnforcementDecision
    4. 决策依据:
       - 无违规 → should_proceed=True
       - 可修正违规 → requires_correction=True
       - 严重违规 → should_proceed=False, 提供safe_response
    5. 记录审计日志
    """)

if __name__ == "__main__":
    engine = trace_actual_constitution_flow()
    if engine:
        analyze_decision_making()
        
        print("\n" + "=" * 70)
        print("✅ 实际流程追踪完成")
        print("\n📌 关键发现:")
        print("   1. 使用load_from_file()而非parse_constitution()")
        print("   2. ConstitutionEngine管理完整生命周期")
        print("   3. EnforcementDecision封装决策结果")
        print("   4. 审计日志记录所有检查")