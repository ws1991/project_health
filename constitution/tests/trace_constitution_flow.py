# trace_constitution_flow.py
"""
追踪宪法系统完整的数据流转过程
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def trace_complete_flow():
    print("🔄 宪法系统完整数据流转追踪")
    print("=" * 70)
    
    # 阶段1: 加载宪法
    print("\n1. 📥 宪法加载阶段")
    from constitution.parser.constitution_parser import ConstitutionParser
    
    parser = ConstitutionParser()
    constitution = parser.parse_constitution("constitution/data/constitution_structured.yaml")
    
    print(f"   • 加载宪法文件: constitution_structured.yaml")
    print(f"   • 解析条款数: {len(constitution.clauses)}")
    print(f"   • 解析规则数: {len(constitution.detection_rules)}")
    
    # 阶段2: 初始化引擎
    print("\n2. ⚙️ 引擎初始化阶段")
    from constitution.engine.constitution_engine import ConstitutionEngine
    
    engine = ConstitutionEngine(constitution)
    print(f"   • 宪法引擎已初始化")
    print(f"   • 规则评估器: {type(engine.rule_evaluator).__name__}")
    
    # 阶段3: 用户输入检查
    print("\n3. 👤 用户输入检查阶段")
    test_queries = [
        "我的血压有点高，应该吃什么药？",
        "分析数据显示平均心率75次/分",
        "这是张三的健康报告，年龄45岁"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   测试用例 {i}: \"{query}\"")
        result = engine.check_input(query)
        
        if result.passed:
            print(f"     结果: ✅ 通过")
        else:
            print(f"     结果: ❌ 拒绝")
            for violation in result.violations:
                print(f"     违规: {violation.clause_id} - {violation.rule_name}")
                if hasattr(violation, 'matched_text'):
                    print(f"     匹配: \"{violation.matched_text}\"")
    
    # 阶段4: 工具输出检查
    print("\n4. 🔧 工具输出检查阶段")
    print("   模拟工具分析输出...")
    
    # 模拟一个工具输出
    tool_output = {
        "summary": "数据分析显示心率偏高，建议进一步检查",
        "metrics": {
            "avg_heart_rate": 85,
            "max_heart_rate": 120
        },
        "observations": "数据显示心率异常"
    }
    
    post_check = engine.check_output(str(tool_output), "分析我的心率数据")
    print(f"   后检查结果: {'✅ 通过' if post_check.passed else '❌ 需要修正'}")
    
    if post_check.corrections:
        print(f"   修正建议: {post_check.corrections}")
    
    # 阶段5: 决策过程
    print("\n5. 🎯 宪法决策过程")
    print("   违规处理策略:")
    
    # 查看宪法的执行策略
    enforcement = constitution.enforcement_strategies
    for level, strategy in enforcement.items():
        print(f"   • {level}: {strategy.get('action', 'unknown')}")
    
    return engine

if __name__ == "__main__":
    try:
        engine = trace_complete_flow()
        print("\n" + "=" * 70)
        print("✅ 数据流转追踪完成")
        print("💡 宪法引擎已就绪，可进行进一步测试")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()