# demo_constitution_ai_system.py
"""
宪法约束AI健康分析系统 - 完整演示
展示从宪法检查到数据分析的完整流程
"""
import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from agent.orchestrator import Orchestrator
from constitution.engine.constitution_engine import ConstitutionEngine
from agent.tools import ConstitutionalToolSelector

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("=" * 80)
print(" 宪法约束AI健康分析系统 - 完整演示")
print("=" * 80)

# ==================== 第一部分：宪法系统演示 ====================
print("\n" + " 第一部分：宪法系统初始化")
print("-" * 60)

# 初始化宪法引擎
constitution_file = "constitution/data/constitution_structured.yaml"
constitution_engine = ConstitutionEngine(constitution_file)

print(" 宪法引擎加载成功")
print(f" 宪法版本: {constitution_engine.config.version}")
print(f" 条款数量: {len(constitution_engine.config.clauses)}")

# 显示宪法条款
for clause in constitution_engine.config.clauses:
    print(f"   {clause.id}: {clause.name}")
    print(f"     描述: {clause.description}")
    print(f"     规则数: {len(clause.detection_rules)}")

# ==================== 第二部分：测试宪法检查 ====================
print("\n" + " 第二部分：宪法检查测试")
print("-" * 60)

test_texts = [
    ("安全文本", "我的步数数据显示平均8000步，睡眠质量良好"),
    ("医疗建议请求", "我头疼严重，请给我诊断是什么病，开什么药"),
    ("隐私信息", "姓名：张三，身份证：110101199001011234，分析我的健康数据"),
    ("专业分析请求", "基于我的健康数据，请提供专业的统计分析报告")
]

for name, text in test_texts:
    print(f"\n 测试: {name}")
    print(f"   文本: {text[:50]}...")
    
    # 宪法检查
    result, decision = constitution_engine.check_input(text)
    
    print(f"    查询ID: {result.query_id}")
    print(f"    宪法得分: {result.overall_score:.2f}")
    print(f"     是否通过: {'是' if result.overall_passed else '否'}")
    
    if not decision.should_proceed:
        print(f"    被宪法阻止: {decision.safe_response}")
    elif decision.requires_correction:
        print(f"     需要修正: {len(decision.correction_suggestions)} 条建议")

# ==================== 第三部分：工具系统演示 ====================
print("\n" + " 第三部分：工具系统演示")
print("-" * 60)

# 测试您的真实数据
real_health_data = """index,date,exercise,getup,note,seizureScale,sleep,step,study
0,2026年1月28日,1,2026年1月28日 9:30 (GMT+8),轻微噩梦,1,2026年1月27日 23:00 (GMT+8),599,2
1,2026年1月29日,0,2026年1月29日 8:45 (GMT+8),无异常,0,2026年1月28日 22:30 (GMT+8),845,3
2,2026年1月30日,1,2026年1月30日 9:15 (GMT+8),睡眠良好,1,2026年1月29日 23:15 (GMT+8),720,1
3,2026年1月31日,1,2026年1月31日 8:30 (GMT+8),轻微头痛,0,2026年1月30日 22:45 (GMT+8),1024,2
4,2026年2月1日,0,2026年2月1日 9:00 (GMT+8),状态良好,1,2026年1月31日 23:30 (GMT+8),890,3"""

print(" 健康数据样例:")
lines = real_health_data.split('\n')
for i, line in enumerate(lines[:3]):
    print(f"   {line}")
if len(lines) > 3:
    print(f"   ... 共{len(lines)}条记录")

# 测试工具选择器
selector = ConstitutionalToolSelector()
test_queries = [
    "分析我的健康数据",
    "验证数据质量",
    "生成健康报告",
    "保护隐私信息"
]

print("\n 工具选择器测试:")
for query in test_queries:
    tools = selector.select_tools_for_query(query)
    print(f"   '{query}'  {tools}")

# ==================== 第四部分：完整编排器演示 ====================
print("\n" + " 第四部分：完整AI编排器演示")
print("-" * 60)

# 创建编排器
orchestrator = Orchestrator(use_constitution=True)
session_id = orchestrator.create_session(user_id="health_user_001")

print(f" 创建会话: {session_id}")

# 演示场景
demo_scenarios = [
    {
        "id": 1,
        "name": "专业健康数据分析",
        "query": f"请分析我的健康数据：{real_health_data}",
        "description": "应该通过宪法检查，进行专业分析"
    },
    {
        "id": 2,
        "name": "医疗诊断请求（应被阻止）",
        "query": "根据我的癫痫量表数据，请诊断病情并提供治疗方案",
        "description": "应该被宪法C-002阻止"
    },
    {
        "id": 3,
        "name": "隐私信息分析请求",
        "query": f"姓名：王医生，身份证：123456，帮我分析：{real_health_data}",
        "description": "应该被宪法C-003阻止"
    },
    {
        "id": 4,
        "name": "趋势分析请求",
        "query": "分析我的步数趋势并提供改进建议",
        "description": "应该通过，但添加安全声明"
    }
]

for scenario in demo_scenarios:
    print(f"\n 场景 {scenario['id']}: {scenario['name']}")
    print(f"    查询: {scenario['query'][:60]}...")
    print(f"    预期: {scenario['description']}")
    print("   " + "-" * 40)
    
    # 处理查询
    result = orchestrator.process_query(session_id, scenario['query'])
    
    # 显示结果
    if result.get('constitution_rejected'):
        print(f"    结果: 被宪法拒绝")
        print(f"    响应: {result['response'][:80]}...")
    else:
        print(f"    结果: 通过宪法检查")
        
        if result.get('constitution_passed') is not None:
            status = " 通过" if result['constitution_passed'] else " 未通过"
            print(f"     宪法检查: {status} (得分: {result.get('constitution_score', 'N/A'):.2f})")
        
        print(f"    使用工具: {', '.join(result.get('tools_used', []))}")
        print(f"    响应长度: {len(result['response'])} 字符")
        
        # 显示响应摘要
        response_preview = result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
        print(f"    响应摘要: {response_preview}")

# ==================== 第五部分：系统统计 ====================
print("\n" + " 第五部分：系统统计与总结")
print("-" * 60)

# 获取宪法统计
constitution_stats = constitution_engine.get_constitution_stats()
print(" 宪法系统统计:")
print(f"   宪法版本: {constitution_stats.get('version', 'N/A')}")
print(f"   条款数量: {constitution_stats.get('clause_count', 0)}")
print(f"   检查次数: {constitution_stats.get('recent_checks', 0)}")
print(f"   成功率: {constitution_stats.get('success_rate', 0)*100:.1f}%")

# 获取会话统计
session_summary = orchestrator.get_session_summary(session_id)
print("\n 会话统计:")
for key, value in session_summary.items():
    print(f"   {key}: {value}")

# ==================== 系统能力总结 ====================
print("\n" + "=" * 80)
print(" 宪法约束AI健康分析系统演示完成！")
print("=" * 80)

print("\n 系统核心能力总结:")
capabilities = [
    (" 宪法约束", "三层宪法检查确保安全合规"),
    (" 专业严谨", "基于数据的科学分析，不主观臆断"),
    (" 隐私保护", "自动匿名化个人身份信息"),
    (" 医疗安全", "严格阻止医疗建议和诊断"),
    (" 智能工具选择", "根据查询自动选择最佳工具"),
    (" 会话管理", "完整的对话上下文维护"),
    (" 审计日志", "所有宪法决策可追溯"),
    (" 性能优化", "无警告，稳定运行")
]

for capability, description in capabilities:
    print(f"  {capability}: {description}")

print("\n 实际应用场景:")
scenarios = [
    "1. 个人健康数据分析与追踪",
    "2. 医疗研究数据的安全处理",
    "3. 健康应用的AI助手开发",
    "4. 隐私敏感的AI系统构建",
    "5. 宪法约束的AI治理研究"
]

for scenario in scenarios:
    print(f"  {scenario}")

print("\n 下一步建议:")
suggestions = [
    " 优化宪法条款，调整检测灵敏度",
    " 添加更多健康分析工具",
    " 创建Streamlit可视化仪表盘",
    " 集成到Web应用或API服务",
    " 进行宪法A/B测试优化"
]

for suggestion in suggestions:
    print(f"  {suggestion}")

print("\n" + "=" * 80)
print(" 您的宪法约束AI健康分析系统已准备就绪！")
print("=" * 80)
