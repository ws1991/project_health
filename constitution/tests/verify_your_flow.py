# constitution/tests/verify_your_flow.py
"""
验证您实际代码中的执行流程
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def verify_your_actual_flow():
    print("🔍 验证您的实际执行流程")
    print("=" * 60)
    
    try:
        # 导入
        from constitution.parser.constitution_parser import ConstitutionParser
        from constitution.rules.detection_rules import KeywordRule
        from constitution.engine.constitution_engine import ConstitutionEngine
        
        # 1. 查看Parser如何工作
        print("\n1. 🔄 ConstitutionParser 工作方式:")
        parser = ConstitutionParser()
        
        # 查看parser的方法
        print(f"   • Parser方法: {[m for m in dir(parser) if not m.startswith('_')]}")
        
        # 2. 模拟YAML中的一个规则
        print("\n2. 📄 模拟YAML规则解析:")
        yaml_rule_data = {
            "name": "test_rule",
            "clause_id": "C-002",
            "rule_type": "keyword",
            "keywords": ["治疗", "开药"],
            "case_sensitive": False
        }
        
        # 查看detection_rules如何创建规则
        rule = KeywordRule(
            name=yaml_rule_data["name"],
            clause_id=yaml_rule_data["clause_id"],
            config=yaml_rule_data
        )
        
        print(f"   • 创建的规则: {rule}")
        print(f"   • 规则名称: {rule.name}")
        print(f"   • 所属条款: {rule.clause_id}")
        print(f"   • 关键词: {rule.keywords}")
        
        # 3. 查看引擎如何使用规则
        print("\n3. ⚙️ 宪法引擎如何使用规则:")
        engine = ConstitutionEngine()
        
        # 查看引擎属性
        print(f"   • 引擎属性: parser={engine.parser}")
        print(f"   • 引擎属性: evaluator={engine.evaluator}")
        
        # 4. 测试规则执行
        print("\n4. 🧪 测试规则执行:")
        test_text = "我需要治疗头痛"
        
        # 直接调用规则的check方法
        matches = rule.check(test_text)
        print(f"   测试文本: \"{test_text}\"")
        print(f"   匹配结果: {matches}")
        
        if matches:
            for match in matches:
                print(f"     → 匹配到: \"{match.get('matched_text', 'N/A')}\"")
        
        print("\n✅ 验证完成！")
        
        # 5. 查看完整流程建议
        print("\n📋 建议的完整流程:")
        print("""
        实际代码建议执行:
        
        1. 创建引擎:
           engine = ConstitutionEngine("constitution/data/constitution_structured.yaml")
        
        2. 检查输入:
           result = engine.check_input("我需要治疗头痛")
        
        3. 根据结果决策:
           if result.should_proceed:
               # 执行工具
               pass
           else:
               # 使用result.safe_response
               pass
        """)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_your_actual_flow()