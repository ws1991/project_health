# interactive_agent_fixed.py
"""
修复后的交互式代理 - 使用正确的API方法名
"""
import sys
from pathlib import Path
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from agent.orchestrator import Orchestrator, HealthDataManager

def display_welcome():
    """显示欢迎信息"""
    print("=" * 70)
    print(" 宪法AI健康分析系统 - 修复版本")
    print("=" * 70)
    print("\n 系统功能：")
    print("   上传和分析您的健康数据（心率、血压、步数等）")
    print("   验证数据质量")
    print("   生成健康报告")
    print("   所有分析都遵循宪法安全原则")
    print("\n 示例命令：")
    print("  1. '分析我的健康数据'")
    print("  2. '上传数据'（然后粘贴CSV）")
    print("  3. '查看数据摘要'")
    print("  4. '验证数据质量'")
    print("  5. '退出'")
    print("-" * 70)

def handle_data_upload(orchestrator, session_id):
    """处理数据上传"""
    print("\n 数据上传模式")
    print("请粘贴您的CSV数据（以空行结束）：")
    
    csv_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            csv_lines.append(line)
        except EOFError:
            break
    
    if csv_lines:
        csv_content = "\n".join(csv_lines)
        print(f"\n 接收数据：{len(csv_lines)}行")
        
        # 验证数据
        data_manager = HealthDataManager()
        validation = data_manager.validate_health_data(csv_content)
        
        if validation.get("valid", False):
            print(f" 数据验证通过：{validation['row_count']}行，{validation['column_count']}列")
            
            # 上传数据
            result = orchestrator.upload_health_data(session_id, csv_content, "手动上传")
            
            if result.get("success", False):
                print(f" 数据已保存：{result.get('file_path')}")
                return " 数据上传成功！您现在可以进行分析了。"
            else:
                return f" 数据保存失败：{result.get('error', '未知错误')}"
        else:
            return f" 数据验证失败：{validation.get('error', '格式错误')}"
    else:
        return " 未提供数据"

def handle_command(orchestrator, session_id, command):
    """处理用户命令"""
    try:
        # 特殊命令处理
        command_lower = command.lower()
        
        if command_lower in ["退出", "exit", "quit", "q"]:
            return None, True
        
        elif command_lower in ["上传数据", "上传", "upload"]:
            response = handle_data_upload(orchestrator, session_id)
            return response, False
        
        elif command_lower in ["数据摘要", "摘要", "summary"]:
            result = orchestrator.get_data_summary(session_id)
            
            if "error" in result:
                return f" {result['error']}", False
            
            summary_text = f" 数据摘要（会话：{session_id}）\n"
            summary_text += f"  数据文件：{len(result.get('data_files', []))}个\n"
            summary_text += f"  总记录数：{result.get('total_records', 0)}条\n"
            
            if result.get("date_range"):
                date_range = result["date_range"]
                summary_text += f"  日期范围：{date_range.get('start')} 到 {date_range.get('end')}\n"
            
            if result.get("columns"):
                columns = result["columns"]
                summary_text += f"  数据列：{', '.join(columns[:5])}"
                if len(columns) > 5:
                    summary_text += f"...等{len(columns)}列"
            
            return summary_text, False
        
        # 处理其他命令
        print(f"\n 正在处理：{command[:50]}...")
        
        # 使用正确的方法名：process_query
        result = orchestrator.process_query(session_id, command)
        
        # 格式化输出
        if result.get("success"):
            response = result.get("response", " 处理完成")
            
            # 添加宪法检查信息
            if result.get("constitution_rejected"):
                response = " " + response
            elif result.get("constitution_passed") is not None:
                constitution_status = "通过 " if result["constitution_passed"] else "未通过 "
                response = f" 宪法检查：{constitution_status}\n\n{response}"
            
            return response, False
        else:
            error_msg = result.get("error", result.get("response", "未知错误"))
            return f" 处理失败：{error_msg}", False
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f" 处理时发生错误：{str(e)}", False

def main():
    """主函数"""
    display_welcome()
    
    # 初始化编排器
    try:
        orchestrator = Orchestrator(use_constitution=True)
        session_id = orchestrator.create_session()
        print(f"\n 会话已创建：{session_id}")
        
        # 检查默认数据
        data_manager = HealthDataManager()
        default_data = data_manager.get_default_health_data()
        if default_data:
            lines = default_data.count('\n')
            print(f" 检测到默认健康数据：{lines}行")
        else:
            print("  未找到默认健康数据，您可以手动上传")
            
    except Exception as e:
        print(f" 系统初始化失败：{e}")
        print("请确保：")
        print("  1. 所有依赖已安装（pip install -r requirements.txt）")
        print("  2. 项目结构完整")
        print("  3. 宪法文件存在：constitution/data/constitution_structured.yaml")
        return
    
    # 主交互循环
    exit_flag = False
    while not exit_flag:
        try:
            # 显示提示符
            print("\n" + "-" * 50)
            user_input = input("您:   ").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            response, should_exit = handle_command(orchestrator, session_id, user_input)
            
            if should_exit:
                print("\n 感谢使用，再见！")
                break
            
            # 显示响应
            print("\nAI:  ", end="")
            if "\n" in response:
                print()  # 换行
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n 用户中断操作")
            break
        except Exception as e:
            print(f"\n 系统错误：{e}")

if __name__ == "__main__":
    main()
