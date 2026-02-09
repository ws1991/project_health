# debug_agent.py
"""
调试版本的交互式代理 - 详细显示执行过程
"""
import sys
from pathlib import Path
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def debug_orchestrator():
    """调试Orchestrator"""
    print("=" * 70)
    print(" 调试Orchestrator执行过程")
    print("=" * 70)
    
    try:
        from agent.orchestrator import Orchestrator
        
        # 创建编排器（禁用宪法简化调试）
        print("\n1.  创建Orchestrator实例...")
        orchestrator = Orchestrator(use_constitution=False)
        session_id = orchestrator.create_session()
        print(f"    会话创建: {session_id}")
        
        # 测试查询
        test_query = "分析我的健康数据"
        print(f"\n2.  测试查询: '{test_query}'")
        
        print("\n3.  调用process_query()...")
        result = orchestrator.process_query(session_id, test_query)
        
        print(f"\n4.  结果分析:")
        print(f"   成功: {result.get('success', False)}")
        print(f"   响应长度: {len(str(result.get('response', '')))}")
        
        if result.get('success'):
            response = result.get('response', '')
            print(f"\n    响应内容 (前200字符):")
            print(f"   {response[:200]}...")
            
            # 显示使用的工具
            if result.get('tools_used'):
                print(f"\n    使用的工具: {result.get('tools_used')}")
        else:
            print(f"\n    错误: {result.get('error', '未知错误')}")
        
        # 尝试启用宪法
        print("\n" + "=" * 50)
        print(" 测试宪法系统...")
        print("=" * 50)
        
        orchestrator_with_constitution = Orchestrator(use_constitution=True)
        session_id2 = orchestrator_with_constitution.create_session()
        
        # 测试安全查询
        safe_query = "分析我的步数数据"
        print(f"\n  安全查询: '{safe_query}'")
        result_safe = orchestrator_with_constitution.process_query(session_id2, safe_query)
        print(f"  结果: {'成功' if result_safe.get('success') else '失败'}")
        
        # 测试不安全查询
        unsafe_query = "诊断我的高血压"
        print(f"\n  不安全查询: '{unsafe_query}'")
        result_unsafe = orchestrator_with_constitution.process_query(session_id2, unsafe_query)
        print(f"  结果: {'被拒绝' if result_unsafe.get('constitution_rejected') else '通过'}")
        
        return True
        
    except Exception as e:
        print(f"\n 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_constitution_engine():
    """调试宪法引擎"""
    print("\n" + "=" * 70)
    print(" 调试宪法引擎")
    print("=" * 70)
    
    try:
        # 添加项目根目录
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from constitution.engine.constitution_engine import ConstitutionEngine
        
        # 创建宪法引擎
        constitution_file = project_root / "constitution" / "data" / "constitution_structured.yaml"
        print(f" 宪法文件: {constitution_file}")
        
        if constitution_file.exists():
            engine = ConstitutionEngine(str(constitution_file))
            print(" 宪法引擎加载成功")
            
            # 测试检查
            test_cases = [
                ("安全的分析请求", "分析我的健康数据"),
                ("医疗建议请求", "我应该吃什么药"),
                ("诊断请求", "诊断我的症状"),
                ("数据分析", "查看我的步数趋势")
            ]
            
            for name, query in test_cases:
                print(f"\n {name}: '{query}'")
                result, decision = engine.check_input(query)
                
                if decision:
                    print(f"   决策: {decision.decision}")
                    print(f"   是否继续: {decision.should_proceed}")
                    if hasattr(decision, 'safe_response'):
                        print(f"   安全响应: {decision.safe_response}")
                else:
                    print(f"   决策对象为空")
                
                if result:
                    print(f"   总体通过: {result.overall_passed}")
                    print(f"   分数: {result.overall_score}")
            
            return True
        else:
            print(f" 宪法文件不存在")
            return False
            
    except Exception as e:
        print(f" 宪法引擎调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_tools():
    """调试工具系统"""
    print("\n" + "=" * 70)
    print(" 调试工具系统")
    print("=" * 70)
    
    try:
        from agent.tools import get_all_tools, execute_tool
        
        # 获取所有工具
        tools = get_all_tools()
        print(f" 可用工具数量: {len(tools)}")
        
        for i, tool_name in enumerate(tools, 1):
            print(f"  {i}. {tool_name}")
        
        # 测试personalized_health_analyzer
        print(f"\n 测试personalized_health_analyzer...")
        
        # 创建测试数据
        test_data = """date,step,exercise,study,sleep
2024-01-01,8000,1,3,7.5
2024-01-02,7500,0,4,8.0
2024-01-03,8200,1,2,7.0"""
        
        result = execute_tool("personalized_health_analyzer", data_csv=test_data)
        print(f" 工具执行: {'成功' if result.get('success') else '失败'}")
        
        if result.get('success'):
            print(f" 分析结果类型: {type(result)}")
            if '详细分析' in result:
                analysis = result['详细分析']
                print(f"   关键指标: {list(analysis.keys())}")
        else:
            print(f" 错误: {result.get('error', '未知错误')}")
        
        return True
        
    except Exception as e:
        print(f" 工具调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主调试函数"""
    print("宪法AI系统 - 详细调试工具")
    print("=" * 70)
    
    options = {
        "1": ("调试Orchestrator", debug_orchestrator),
        "2": ("调试宪法引擎", debug_constitution_engine),
        "3": ("调试工具系统", debug_tools),
        "4": ("运行完整测试", lambda: all([
            debug_orchestrator(),
            debug_constitution_engine(),
            debug_tools()
        ]))
    }
    
    while True:
        print("\n请选择调试项目：")
        for key, (name, _) in options.items():
            print(f"  {key}. {name}")
        print("  0. 退出")
        
        choice = input("\n请输入选择: ").strip()
        
        if choice == "0":
            print("\n 调试结束")
            break
        elif choice in options:
            print(f"\n{'='*60}")
            print(f"开始调试: {options[choice][0]}")
            print(f"{'='*60}")
            options[choice][1]()
        else:
            print(" 无效选择")
        
        input("\n按Enter键继续...")

if __name__ == "__main__":
    main()
