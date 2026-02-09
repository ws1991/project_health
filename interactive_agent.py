# interactive_agent.py (更新版)
"""
AI健康数据分析智能体 - 交互模式
使用完整的Orchestrator架构
"""
import sys
import os
from datetime import datetime
from pathlib import Path
# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("🤖 AI健康数据分析智能体 - 宪法约束版")
    print("=" * 60)
    print()
    
    try:
        # 导入编排器
        from agent.orchestrator import Orchestrator
        
        # 创建编排器实例
        orchestrator = Orchestrator()
        
        print("✅ 系统初始化完成")
        print(f"📦 加载了 {len(orchestrator.tools)} 个宪法约束工具")
        print()
        
        # 显示欢迎信息
        welcome_msg = """
欢迎使用AI健康数据分析智能体！

本系统在严格的宪法约束下运行，确保：
1. ⚖️ 所有分析遵循健康数据分析宪法
2. 🔒 数据隐私和安全得到保护  
3. ⚠️ 包含明确的安全声明
4. 💡 提供基于数据的观察建议（非医疗建议）

可用命令：
• '帮助' - 显示所有命令
• '状态' - 查看系统状态
• '宪法健康数据分析 [文件路径]' - 宪法约束分析
• '加载数据 [文件路径]' - 加载健康数据
• '生成报告 [文件路径]' - 生成完整报告
• '退出' - 退出系统

示例：
  宪法健康数据分析 data/sample_health_data.csv
  加载数据 data/我的健康数据.csv
"""
        print(welcome_msg)
        
        # 交互循环
        session_id = None
        conversation_history = []
        
        while True:
            try:
                user_input = input("\\n您: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['退出', 'exit', 'quit', 'q']:
                    print("\\n感谢使用，再见！")
                    break
                
                # 记录对话
                conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                
                # 处理请求
                result = orchestrator.process_request(user_input, session_id)
                
                # 更新会话ID
                if 'session_id' in result:
                    session_id = result['session_id']
                
                # 显示结果
                print(f"\\n{'=' * 40}")
                
                if result.get('success'):
                    response = result.get('response', '')
                    print(f"🤖 {response}")
                    
                    # 显示建议
                    suggestions = result.get('suggestions', [])
                    if suggestions:
                        print(f"\\n💡 建议:")
                        for suggestion in suggestions:
                            print(f"  • {suggestion}")
                    
                    # 记录系统响应
                    conversation_history.append({
                        "role": "system",
                        "content": response[:500],
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
                    
                else:
                    error_msg = result.get('error', '未知错误')
                    print(f"❌ {error_msg}")
                    
                    suggestion = result.get('suggestion')
                    if suggestion:
                        print(f"💡 {suggestion}")
                
                # 如果需要澄清
                if result.get('needs_clarification'):
                    clarification = result.get('message', '')
                    print(f"\\n❓ {clarification}")
                    
                    clarification_input = input("请输入: ").strip()
                    if clarification_input:
                        # 组合请求
                        combined_input = f"{user_input} {clarification_input}"
                        clarification_result = orchestrator.process_request(combined_input, session_id)
                        
                        if clarification_result.get('success'):
                            print(f"\\n✅ {clarification_result.get('response', '')}")
                        else:
                            print(f"\\n❌ {clarification_result.get('error', '')}")
                
                print(f"{'=' * 40}")
                
            except KeyboardInterrupt:
                print("\\n\\n检测到中断，退出系统...")
                break
            except Exception as e:
                print(f"\\n❌ 处理错误: {e}")
                import traceback
                traceback.print_exc()
        
        # 显示会话总结
        if conversation_history:
            print(f"\\n📊 本次会话统计:")
            print(f"  对话轮次: {len([m for m in conversation_history if m['role'] == 'user'])}")
            print(f"  总消息数: {len(conversation_history)}")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保以下文件存在:")
        print("  - agent/orchestrator.py")
        print("  - agent/tools.py")
        print("  - agent/constitution.txt")
        print("\\n解决方案:")
        print("  1. 检查文件路径")
        print("  2. 运行: pip install -r requirements.txt")
        print("  3. 重新启动系统")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()