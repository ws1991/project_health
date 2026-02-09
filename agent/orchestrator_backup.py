# agent/orchestrator.py
"""
健康数据智能体编排器
作为智能体的"大脑"，协调工具调用、宪法遵循和状态管理
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# 导入工具
from agent.tools import get_all_tools


class AgentState(Enum):
    """智能体状态枚举"""
    IDLE = "IDLE"              # 空闲状态
    PROCESSING = "PROCESSING"  # 处理中
    WAITING_FOR_CLARIFICATION = "WAITING_FOR_CLARIFICATION"  # 等待澄清
    ERROR = "ERROR"            # 错误状态
    COMPLETED = "COMPLETED"    # 完成状态


@dataclass
class AgentContext:
    """智能体对话上下文"""
    session_id: str
    user_id: str = "default_user"
    conversation_history: List[Dict] = None
    current_state: AgentState = AgentState.IDLE
    last_interaction: datetime = None
    preferences: Dict[str, Any] = None
    data_files: List[str] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.preferences is None:
            self.preferences = {}
        if self.data_files is None:
            self.data_files = []
        if self.last_interaction is None:
            self.last_interaction = datetime.now()
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_interaction = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "state": self.current_state.value,
            "message_count": len(self.conversation_history),
            "last_interaction": self.last_interaction.isoformat(),
            "data_files": self.data_files
        }


class HealthDataAgentOrchestrator:
    """
    健康数据智能体编排器
    
    核心职责：
    1. 接收和解析用户请求
    2. 确保宪法遵循（L2层约束）
    3. 路由到合适的工具
    4. 管理对话状态和上下文
    5. 处理错误和异常
    """
    
    def __init__(self, constitution_path: str = None):
        """
        初始化编排器
        
        Args:
            constitution_path: 宪法文件路径
        """
        # 1. 加载工具
        self.tools = get_all_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # 2. 加载宪法
        self.constitution = self._load_constitution(constitution_path)
        
        # 3. 初始化状态
        self.state = AgentState.IDLE
        self.contexts: Dict[str, AgentContext] = {}
        
        # 4. 设置日志
        self.logger = self._setup_logging()
        
        # 5. 命令映射
        self.command_map = self._build_command_map()
        
        self.logger.info(f"✅ 编排器初始化完成，加载了 {len(self.tools)} 个工具")
        self.logger.info(f"📜 宪法已加载，长度: {len(self.constitution)} 字符")
    
    def _load_constitution(self, constitution_path: str = None) -> str:
        """加载宪法文件"""
        if constitution_path is None:
            constitution_path = os.path.join(
                os.path.dirname(__file__), 
                'constitution.txt'
            )
        
        try:
            with open(constitution_path, 'r', encoding='utf-8') as f:
                constitution = f.read()
            return constitution
        except FileNotFoundError:
            self.logger.warning(f"宪法文件未找到: {constitution_path}")
            return "# 默认宪法\n确保所有分析安全、准确、符合伦理。"
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger("HealthDataAgentOrchestrator")
        logger.setLevel(logging.INFO)
        
        # 创建logs目录
        os.makedirs("logs", exist_ok=True)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            f"logs/orchestrator_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _build_command_map(self) -> Dict[str, Dict]:
        """构建命令映射表"""
        return {
            "宪法分析": {
                "description": "宪法约束的健康数据分析",
                "tool_name": "constitutional_health_analysis",
                "constitution_check": True,
                "requires_file": True
            },
            "加载数据": {
                "description": "加载健康数据文件",
                "tool_name": "load_health_data_constitutional",
                "constitution_check": True,
                "requires_file": True
            },
            "发作分析": {
                "description": "宪法约束的发作模式分析",
                "tool_name": "constitutional_seizure_analysis",
                "constitution_check": True,
                "requires_file": True
            },
            "生成报告": {
                "description": "生成完整的宪法约束分析报告",
                "tool_name": "generate_constitutional_report",
                "constitution_check": True,
                "requires_file": True
            },
            "帮助": {
                "description": "显示帮助信息",
                "tool_name": None,
                "constitution_check": False,
                "requires_file": False
            },
            "状态": {
                "description": "显示系统状态",
                "tool_name": None,
                "constitution_check": False,
                "requires_file": False
            }
        }
    
    def _get_or_create_context(self, session_id: str = None) -> AgentContext:
        """获取或创建对话上下文"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if session_id not in self.contexts:
            self.contexts[session_id] = AgentContext(session_id=session_id)
            self.logger.info(f"创建新会话: {session_id}")
        
        return self.contexts[session_id]
    
    def _check_constitution_compliance(self, user_input: str, context: AgentContext) -> Tuple[bool, str]:
        """
        检查宪法合规性
        
        Returns:
            Tuple[通过检查, 错误信息或""]
        """
        # 1. 基本安全检查
        forbidden_patterns = [
            "诊断", "治疗", "处方", "开药", "手术",
            "保证治愈", "100%有效", "绝对安全"
        ]
        
        for pattern in forbidden_patterns:
            if pattern in user_input:
                return False, f"输入包含禁止词汇: '{pattern}'，根据宪法拒绝处理"
        
        # 2. 数据隐私检查
        if "分享数据" in user_input or "上传数据" in user_input:
            return False, "根据宪法，禁止分享或上传个人健康数据"
        
        # 3. 医疗建议检查
        if "我应该" in user_input and any(word in user_input for word in ["吃药", "治疗", "手术"]):
            return False, "根据宪法，不能提供具体的医疗建议"
        
        return True, ""
    
    def _extract_file_path(self, user_input: str) -> Optional[str]:
        """从用户输入中提取文件路径"""
        import re
        
        # 匹配常见的文件路径模式
        patterns = [
            r'[\"\'“”]([^\"\'“”]+\.csv)[\"\'“”]',  # 引号内的.csv文件
            r'data/[^ \n]+\.csv',  # data/开头的.csv文件
            r'[A-Za-z]:\\[^ \n]+\.csv',  # Windows路径
            r'/[^ \n]+\.csv',  # Unix路径
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                file_path = match.group(0) if match.group(0) else match.group(1)
                # 清理引号
                file_path = file_path.strip('\"\'"')
                return file_path
        
        return None
    
    def _parse_user_intent(self, user_input: str) -> Dict[str, Any]:
        """解析用户意图"""
        user_input_lower = user_input.lower()
        
        # 匹配命令
        for command, config in self.command_map.items():
            if command in user_input or any(keyword in user_input_lower for keyword in config.get("keywords", [])):
                return {
                    "command": command,
                    "config": config,
                    "confidence": 0.9
                }
        
        # 检测文件路径
        file_path = self._extract_file_path(user_input)
        if file_path:
            return {
                "command": "宪法分析",  # 默认命令
                "config": self.command_map["宪法分析"],
                "file_path": file_path,
                "confidence": 0.7
            }
        
        # 默认：通用分析
        if "分析" in user_input or "看一下" in user_input or "查看" in user_input:
            return {
                "command": "宪法分析",
                "config": self.command_map["宪法分析"],
                "confidence": 0.6
            }
        
        # 未知意图
        return {
            "command": None,
            "config": None,
            "confidence": 0.0,
            "message": "未识别命令，请明确您的需求"
        }
    
    def _execute_tool(self, tool_name: str, **kwargs) -> str:
        """执行工具"""
        if tool_name not in self.tool_map:
            return f"❌ 工具 '{tool_name}' 不存在"
        
        try:
            tool = self.tool_map[tool_name]
            result = tool.func(**kwargs)
            return result
        except Exception as e:
            self.logger.error(f"工具执行失败: {tool_name}, 错误: {e}")
            return f"❌ 工具执行失败: {str(e)}"
    
    def _format_response(self, result: Any, context: AgentContext, intent: Dict) -> Dict[str, Any]:
        """格式化响应"""
        response = {
            "success": True,
            "session_id": context.session_id,
            "state": context.current_state.value,
            "timestamp": datetime.now().isoformat(),
            "response": result if isinstance(result, str) else str(result),
            "suggestions": []
        }
        
        # 根据意图添加建议
        if intent.get("command") == "宪法分析":
            response["suggestions"].append("💡 您可以尝试 '生成报告' 获取完整分析")
            response["suggestions"].append("📊 或者输入其他数据文件路径进行分析")
        
        elif intent.get("command") == "加载数据":
            response["suggestions"].append("💡 数据加载成功，现在可以尝试 '宪法分析'")
        
        # 添加宪法提醒
        if intent.get("config", {}).get("constitution_check", False):
            response["constitution_compliant"] = True
            response["safety_disclaimer"] = "本分析遵循健康数据分析宪法，不构成医疗建议"
        
        return response
    
    def process_request(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """
        处理用户请求的主入口
        
        Args:
            user_input: 用户输入文本
            session_id: 会话ID（可选）
            
        Returns:
            处理结果字典
        """
        self.logger.info(f"处理请求: '{user_input[:50]}...'")
        
        try:
            # 1. 状态转换：空闲 -> 处理中
            self.state = AgentState.PROCESSING
            
            # 2. 获取或创建上下文
            context = self._get_or_create_context(session_id)
            context.current_state = AgentState.PROCESSING
            context.add_message("user", user_input)
            
            # 3. 宪法合规性检查
            compliance_ok, compliance_msg = self._check_constitution_compliance(user_input, context)
            if not compliance_ok:
                self.state = AgentState.ERROR
                context.current_state = AgentState.ERROR
                context.add_message("system", f"宪法检查失败: {compliance_msg}")
                
                return {
                    "success": False,
                    "error": compliance_msg,
                    "constitution_violation": True,
                    "session_id": context.session_id,
                    "suggestion": "请修改输入，确保符合健康数据分析宪法"
                }
            
            # 4. 解析用户意图
            intent = self._parse_user_intent(user_input)
            self.logger.info(f"解析意图: {intent.get('command', '未知')}, 置信度: {intent.get('confidence', 0)}")
            
            # 5. 处理特殊命令
            if intent["command"] == "帮助":
                help_text = "🤖 可用命令:\n"
                for cmd, config in self.command_map.items():
                    help_text += f"  • {cmd}: {config['description']}\n"
                help_text += "\n💡 示例:\n"
                help_text += "  '分析 data/sample.csv'\n"
                help_text += "  '宪法健康数据分析'\n"
                help_text += "  '生成完整报告'"
                
                context.add_message("system", help_text)
                context.current_state = AgentState.COMPLETED
                self.state = AgentState.IDLE
                
                return self._format_response(help_text, context, intent)
            
            elif intent["command"] == "状态":
                status_info = {
                    "系统状态": self.state.value,
                    "活跃会话": len(self.contexts),
                    "可用工具": len(self.tools),
                    "当前会话": context.to_dict()
                }
                status_text = json.dumps(status_info, ensure_ascii=False, indent=2)
                
                context.add_message("system", status_text)
                context.current_state = AgentState.COMPLETED
                self.state = AgentState.IDLE
                
                return self._format_response(status_text, context, intent)
            
            # 6. 检查是否需要文件
            config = intent.get("config", {})
            if config.get("requires_file", False):
                file_path = intent.get("file_path")
                if not file_path:
                    # 请求文件路径
                    context.current_state = AgentState.WAITING_FOR_CLARIFICATION
                    self.state = AgentState.WAITING_FOR_CLARIFICATION
                    
                    clarification = "📁 请提供数据文件路径 (如: data/sample_health_data.csv):"
                    context.add_message("system", clarification)
                    
                    return {
                        "success": True,
                        "needs_clarification": True,
                        "clarification_type": "file_path",
                        "message": clarification,
                        "session_id": context.session_id
                    }
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    context.current_state = AgentState.ERROR
                    self.state = AgentState.ERROR
                    
                    error_msg = f"❌ 文件不存在: {file_path}"
                    context.add_message("system", error_msg)
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "session_id": context.session_id,
                        "suggestion": "请检查文件路径是否正确"
                    }
                
                # 记录文件使用
                if file_path not in context.data_files:
                    context.data_files.append(file_path)
            
            # 7. 执行工具
            tool_name = config.get("tool_name")
            if not tool_name:
                context.current_state = AgentState.ERROR
                self.state = AgentState.ERROR
                
                error_msg = "❌ 未找到对应的工具"
                context.add_message("system", error_msg)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "session_id": context.session_id
                }
            
            # 准备工具参数
            tool_kwargs = {}
            if intent.get("file_path"):
                tool_kwargs["file_path"] = intent["file_path"]
            
            # 执行工具
            self.logger.info(f"执行工具: {tool_name}, 参数: {tool_kwargs}")
            result = self._execute_tool(tool_name, **tool_kwargs)
            
            # 8. 更新状态和记录
            context.add_message("system", result[:200] + "..." if len(result) > 200 else result)
            context.current_state = AgentState.COMPLETED
            self.state = AgentState.IDLE
            
            # 9. 格式化响应
            response = self._format_response(result, context, intent)
            self.logger.info(f"请求处理完成，会话: {context.session_id}")
            
            return response
            
        except Exception as e:
            # 错误处理
            self.logger.error(f"处理请求时发生错误: {e}", exc_info=True)
            self.state = AgentState.ERROR
            
            if 'context' in locals():
                context.current_state = AgentState.ERROR
                context.add_message("system", f"系统错误: {str(e)}")
            
            return {
                "success": False,
                "error": f"系统内部错误: {str(e)}",
                "session_id": session_id if 'context' not in locals() else context.session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        if session_id in self.contexts:
            context = self.contexts[session_id]
            return {
                "session_id": session_id,
                "state": context.current_state.value,
                "message_count": len(context.conversation_history),
                "data_files": context.data_files,
                "last_interaction": context.last_interaction.isoformat()
            }
        return None
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理旧会话"""
        now = datetime.now()
        sessions_to_remove = []
        
        for session_id, context in self.contexts.items():
            age = now - context.last_interaction
            if age.total_seconds() > max_age_hours * 3600:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.contexts[session_id]
            self.logger.info(f"清理旧会话: {session_id}")
        
        return len(sessions_to_remove)


# 导出类
__all__ = ['HealthDataAgentOrchestrator', 'AgentState', 'AgentContext']


# 测试代码
if __name__ == "__main__":
    print("🧪 HealthDataAgentOrchestrator 测试")
    print("=" * 60)
    
    # 创建编排器实例
    orchestrator = HealthDataAgentOrchestrator()
    
    # 测试1: 帮助命令
    print("\n1. 测试帮助命令:")
    result = orchestrator.process_request("帮助")
    print(f"结果: {result.get('success', False)}")
    print(f"响应: {result.get('response', '')[:100]}...")
    
    # 测试2: 状态命令
    print("\n2. 测试状态命令:")
    result = orchestrator.process_request("状态")
    print(f"结果: {result.get('success', False)}")
    
    # 测试3: 宪法检查
    print("\n3. 测试宪法检查（违规输入）:")
    result = orchestrator.process_request("我应该吃什么药治疗")
    print(f"结果: {result.get('success', False)}")
    print(f"错误: {result.get('error', '')}")
    
    print("\n✅ 编排器测试完成")