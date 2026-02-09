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
from  pathlib import Path
# 导入工具
from agent.tools import get_all_tools

# 在 orchestrator.py 中添加以下类
class HealthDataManager:
    """健康数据管理器"""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        
        # 确保目录存在
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    def get_default_health_data(self) -> Optional[str]:
        """获取默认的健康数据（您的health.csv）"""
        default_file = self.raw_data_dir / "health.csv"
        
        if default_file.exists():
            try:
                with open(default_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"读取默认数据失败: {e}")
                return None
        else:
            self.logger.warning(f"默认数据文件不存在: {default_file}")
            return None
    
    def extract_csv_from_query(self, query: str) -> Optional[str]:
        """从查询中提取CSV数据"""
        import re
        
        # 模式1：CSV块
        csv_pattern = r'```(?:csv)?\s*([\s\S]*?)\s*```'
        csv_matches = re.findall(csv_pattern, query)
        if csv_matches:
            return csv_matches[0].strip()
        
        # 模式2：直接粘贴的CSV数据（包含表头）
        lines = query.strip().split('\n')
        if len(lines) > 2 and ',' in lines[0]:  # 第一行有逗号，可能是CSV表头
            # 检查是否是有效的CSV格式
            expected_columns = ['date', 'exercise', 'getup', 'note', 'seizureScale', 'sleep', 'step', 'study']
            first_line_cols = lines[0].split(',')
            
            # 如果表头匹配或部分匹配
            if any(col in first_line_cols for col in expected_columns):
                return '\n'.join(lines)
        
        return None
    
    def save_user_data(self, session_id: str, csv_content: str, data_type: str = "user_upload") -> str:
        """保存用户上传的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{data_type}_{timestamp}.csv"
        filepath = self.raw_data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            self.logger.info(f"用户数据已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"保存用户数据失败: {e}")
            return None
    
    def get_session_data_files(self, session_id: str) -> List[str]:
        """获取会话相关的数据文件"""
        session_files = []
        
        # 默认数据文件
        default_file = self.raw_data_dir / "health.csv"
        if default_file.exists():
            session_files.append(str(default_file))
        
        # 查找该会话上传的文件
        pattern = f"{session_id}_*.csv"
        for file in self.raw_data_dir.glob(pattern):
            session_files.append(str(file))
        
        return session_files
    
    def merge_health_data(self, default_data: str, user_data: str = None) -> str:
        """合并默认数据和用户数据"""
        try:
            import pandas as pd
            from io import StringIO
            
            # 读取默认数据
            default_df = pd.read_csv(StringIO(default_data))
            
            if user_data:
                # 读取用户数据
                user_df = pd.read_csv(StringIO(user_data))
                
                # 合并数据（去重）
                combined_df = pd.concat([default_df, user_df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
                
                # 按日期排序
                combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
                combined_df = combined_df.sort_values('date')
                combined_df['date'] = combined_df['date'].dt.strftime('%Y-%m-%d')
                
                return combined_df.to_csv(index=False)
            else:
                return default_data
                
        except Exception as e:
            self.logger.error(f"合并数据失败: {e}")
            return default_data
    
    def validate_health_data(self, csv_content: str) -> Dict[str, Any]:
        """验证健康数据格式"""
        try:
            import pandas as pd
            from io import StringIO
            
            df = pd.read_csv(StringIO(csv_content))
            
            validation_result = {
                "valid": True,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "date_range": None,
                "missing_values": {}
            }
            
            # 检查必需列
            required_columns = ['date', 'step']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                validation_result["valid"] = False
                validation_result["missing_columns"] = missing_columns
            
            # 检查日期列
            if 'date' in df.columns:
                try:
                    dates = pd.to_datetime(df['date'], errors='coerce')
                    valid_dates = dates.notna().sum()
                    validation_result["date_validity"] = f"{valid_dates}/{len(df)}"
                    
                    if valid_dates > 0:
                        validation_result["date_range"] = {
                            "start": dates.min().strftime('%Y-%m-%d'),
                            "end": dates.max().strftime('%Y-%m-%d')
                        }
                except:
                    validation_result["date_validity"] = "格式错误"
            
            # 检查数值列
            numeric_columns = ['step', 'exercise', 'study', 'seizureScale']
            for col in numeric_columns:
                if col in df.columns:
                    numeric_values = pd.to_numeric(df[col], errors='coerce')
                    valid_count = numeric_values.notna().sum()
                    validation_result["missing_values"][col] = f"{valid_count}/{len(df)}"
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
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
            "conversation_history": self.conversation_history,
            "current_state": self.current_state.value,
            "last_interaction": self.last_interaction.isoformat(),
            "preferences": self.preferences,
            "data_files": self.data_files
        }


class Orchestrator:
    """智能体编排器"""
    def __init__(self, use_constitution: bool = True, data_dir: str = "data"):
        """初始化编排器"""
        self.logger = logging.getLogger(__name__)
        self.tools = get_all_tools()
        self.sessions: Dict[str, AgentContext] = {}
        
        # 数据管理器
        self.data_manager = HealthDataManager(data_dir)
        
        # 宪法系统集成
        self.use_constitution = use_constitution
        self.constitution_engine = None
        
        if use_constitution:
            try:
                # 添加项目根目录到路径
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.append(project_root)
                
                from constitution.engine.constitution_engine import ConstitutionEngine
                
                constitution_file = os.path.join(project_root, "constitution", "data", "constitution_structured.yaml")
                if os.path.exists(constitution_file):
                    self.constitution_engine = ConstitutionEngine(constitution_file)
                    self.logger.info(" 宪法引擎加载成功")
                else:
                    self.logger.warning(f" 宪法文件不存在: {constitution_file}")
                    self.use_constitution = False
                    
            except ImportError as e:
                self.logger.warning(f" 宪法模块未安装: {e}")
                self.use_constitution = False
        
        self.logger.info(f"编排器初始化完成，工具数量: {len(self.tools)}, 宪法系统: {'启用' if self.use_constitution else '禁用'}")
        
        self.logger.info(f"编排器初始化完成，数据目录: {data_dir}")
    # 在 Orchestrator 类中添加方法
    def upload_health_data(self, session_id: str, csv_content: str, 
                        description: str = "用户上传") -> Dict[str, Any]:
        """上传健康数据"""
        
        context = self.get_session(session_id)
        if not context:
            return {
                "success": False,
                "error": "会话不存在"
            }
        
        # 验证数据格式
        validation = self.data_manager.validate_health_data(csv_content)
        
        if not validation.get("valid", False):
            return {
                "success": False,
                "error": "数据格式无效",
                "validation_details": validation
            }
        
        # 保存数据
        saved_file = self.data_manager.save_user_data(session_id, csv_content, description)
        
        if saved_file:
            context.data_files.append(saved_file)
            
            return {
                "success": True,
                "message": f"数据上传成功，共{validation['row_count']}条记录",
                "file_path": saved_file,
                "validation": validation
            }
        else:
            return {
                "success": False,
                "error": "数据保存失败"
            }

    def get_data_summary(self, session_id: str) -> Dict[str, Any]:
        """获取数据摘要"""
        
        context = self.get_session(session_id)
        if not context:
            return {"error": "会话不存在"}
        
        summary = {
            "session_id": session_id,
            "data_files": [],
            "total_records": 0,
            "date_range": None
        }
        
        # 分析所有数据文件
        all_data = []
        default_data = self.data_manager.get_default_health_data()
        
        if default_data:
            all_data.append(default_data)
        
        for file_path in context.data_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = f.read()
                    all_data.append(file_data)
            except:
                continue
        
        # 合并和分析所有数据
        if all_data:
            try:
                import pandas as pd
                from io import StringIO
                
                # 合并所有数据
                combined_df = None
                for data in all_data:
                    df = pd.read_csv(StringIO(data))
                    if combined_df is None:
                        combined_df = df
                    else:
                        combined_df = pd.concat([combined_df, df], ignore_index=True)
                
                if combined_df is not None:
                    # 去重并排序
                    if 'date' in combined_df.columns:
                        combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
                        combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
                        combined_df = combined_df.sort_values('date')
                        
                        summary["total_records"] = len(combined_df)
                        if combined_df['date'].notna().any():
                            summary["date_range"] = {
                                "start": combined_df['date'].min().strftime('%Y-%m-%d'),
                                "end": combined_df['date'].max().strftime('%Y-%m-%d')
                            }
                    
                    summary["columns"] = combined_df.columns.tolist()
                    summary["data_files"] = context.data_files
                    
            except Exception as e:
                summary["error"] = f"数据分析失败: {e}"
        
        return summary
    def create_session(self, session_id: str = None, user_id: str = "default_user") -> str:
        """创建新会话"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now()) % 10000:04d}"
        
        context = AgentContext(
            session_id=session_id,
            user_id=user_id
        )
        
        self.sessions[session_id] = context
        self.logger.info(f"创建新会话: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[AgentContext]:
        """获取会话上下文"""
        return self.sessions.get(session_id)
    
    def process_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """处理用户查询"""
        # 获取或创建会话
        context = self.get_session(session_id)
        if not context:
            session_id = self.create_session(session_id)
            context = self.sessions[session_id]
        
        # 更新状态
        context.current_state = AgentState.PROCESSING
        context.add_message("user", query)
        
        self.logger.info(f"处理查询: 会话={session_id}, 查询长度={len(query)}")
        
        try:
            # 1. 宪法预检查（如果启用）
            constitution_check_result = None
            constitution_decision = None
            
            if self.use_constitution and self.constitution_engine:
                self.logger.info("执行宪法预检查...")
                constitution_check_result, constitution_decision = self.constitution_engine.check_input(query)
                
                if not constitution_decision.should_proceed:
                    # 被宪法拒绝
                    response = constitution_decision.safe_response or "抱歉，根据安全政策，我无法处理这个请求。"
                    
                    context.add_message("assistant", response)
                    context.current_state = AgentState.COMPLETED
                    
                    return {
                        "success": False,
                        "response": response,
                        "constitution_rejected": True,
                        "session_id": session_id,
                        "state": context.current_state.value
                    }
            
            # 2. 选择和执行工具（简化版）
            self.logger.info("选择和执行工具...")
            tool_result = self._execute_tools(context, query, constitution_decision)
            
            # 3. 宪法后检查（如果启用）
            if self.use_constitution and self.constitution_engine and constitution_check_result:
                self.logger.info("执行宪法后检查...")
                post_check_result = self.constitution_engine.check_output(
                    tool_result["response"], 
                    constitution_check_result.query_id
                )
                
                if post_check_result.requires_correction:
                    self.logger.info("应用宪法修正...")
                    tool_result["response"] = self.constitution_engine.apply_constitutional_corrections(
                        tool_result["response"], post_check_result
                    )
            
            # 4. 更新上下文
            context.add_message("assistant", tool_result["response"])
            context.current_state = AgentState.COMPLETED
            
            # 5. 构建响应
            result = {
                "success": True,
                "response": tool_result["response"],
                "session_id": session_id,
                "state": context.current_state.value,
                "tools_used": tool_result.get("tools_used", []),
                "constitution_checked": self.use_constitution
            }
            
            if constitution_check_result:
                result["constitution_passed"] = constitution_check_result.overall_passed
                result["constitution_score"] = constitution_check_result.overall_score
            
            return result
            
        except Exception as e:
            self.logger.error(f"处理查询时出错: {e}", exc_info=True)
            context.current_state = AgentState.ERROR
            
            error_response = f"抱歉，处理请求时出现错误: {str(e)}"
            context.add_message("assistant", error_response)
            
            return {
                "success": False,
                "response": error_response,
                "error": str(e),
                "session_id": session_id,
                "state": context.current_state.value
            }
    
    def _execute_tools(self, context: AgentContext, query: str, 
                    constitution_decision: Any = None) -> Dict[str, Any]:
        """执行工具 - 集成数据管理器"""
        
        try:
            # 1. 获取数据
            analysis_data = self._prepare_analysis_data(context, query)
            
            if not analysis_data:
                return {
                    "response": "无法获取分析数据。请提供CSV格式的健康数据，或确保data/raw/health.csv文件存在。",
                    "tools_used": [],
                    "data_available": False
                }
            
            # 2. 选择工具
            from agent.tools import ConstitutionalToolSelector, execute_tool
            
            selector = ConstitutionalToolSelector()
            selected_tools = selector.select_tools_for_query(query, constitution_decision)
            
            # 3. 执行工具
            results = []
            tools_used = []
            
            for tool_name in selected_tools[:2]:  # 最多执行2个工具
                try:
                    self.logger.info(f"执行工具: {tool_name}")
                    
                    # 根据工具类型传递参数
                    if tool_name == "personalized_health_analyzer":
                        result = execute_tool(tool_name, data_csv=analysis_data)
                    elif tool_name == "csv_data_validator":
                        result = execute_tool(tool_name, csv_content=analysis_data)
                    elif tool_name == "generate_health_report":
                        result = execute_tool(tool_name, csv_data=analysis_data)
                    elif tool_name == "data_statistics_analysis":
                        # 将CSV保存为临时文件
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                            f.write(analysis_data)
                            temp_file = f.name
                        
                        result = execute_tool(tool_name, file_path=temp_file)
                        
                        # 清理临时文件
                        import os
                        os.unlink(temp_file)
                    else:
                        # 其他工具使用默认参数
                        result = execute_tool(tool_name, query=query)
                    
                    if result.get("success", False):
                        results.append(result)
                        tools_used.append(tool_name)
                        
                        self.logger.info(f"工具 {tool_name} 执行成功")
                    else:
                        self.logger.warning(f"工具 {tool_name} 执行失败: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    self.logger.error(f"执行工具 {tool_name} 时出错: {e}")
            
            # 4. 格式化结果
            response = self._format_tool_results(results, query)
            
            # 5. 更新上下文数据文件列表
            self._update_context_data_files(context)
            
            return {
                "response": response,
                "tools_used": tools_used,
                "data_available": True,
                "raw_results": results
            }
            
        except Exception as e:
            self.logger.error(f"执行工具时出错: {e}")
            return {
                "response": f"执行分析时出现错误: {str(e)}",
                "tools_used": [],
                "error": str(e)
            }

    def _prepare_analysis_data(self, context: AgentContext, query: str) -> Optional[str]:
        """准备分析数据"""
        
        # 1. 尝试从查询中提取CSV数据
        query_data = self.data_manager.extract_csv_from_query(query)
        
        # 2. 获取默认的健康数据
        default_data = self.data_manager.get_default_health_data()
        
        if not default_data:
            self.logger.warning("默认健康数据不存在")
            # 如果没有默认数据，只使用查询中的数据
            return query_data
        
        # 3. 合并数据
        if query_data:
            # 验证用户数据
            validation = self.data_manager.validate_health_data(query_data)
            if validation.get("valid", False):
                # 保存用户数据
                saved_file = self.data_manager.save_user_data(
                    context.session_id, 
                    query_data, 
                    "query_extracted"
                )
                if saved_file:
                    context.data_files.append(saved_file)
                
                # 合并数据
                merged_data = self.data_manager.merge_health_data(default_data, query_data)
                self.logger.info(f"使用合并数据: 默认{len(default_data.splitlines())}行 + 用户{len(query_data.splitlines())}行")
                return merged_data
            else:
                self.logger.warning(f"查询数据验证失败: {validation}")
                # 验证失败，只使用默认数据
                return default_data
        else:
            # 没有查询数据，只使用默认数据
            self.logger.info(f"使用默认数据: {len(default_data.splitlines())}行")
            return default_data

    def _format_tool_results(self, results: List[Dict], original_query: str) -> str:
        """格式化工具结果"""
        
        if not results:
            return "未能生成分析结果。"
        
        response_parts = []
        response_parts.append(f"📊 **健康数据分析报告**")
        response_parts.append(f"*基于您的查询: \"{original_query[:50]}{'...' if len(original_query) > 50 else ''}\"*")
        response_parts.append("")
        
        for i, result in enumerate(results, 1):
            tool_name = result.get("tool", "未知工具")
            
            response_parts.append(f"**{i}. {tool_name}**")
            
            if tool_name == "personalized_health_analyzer":
                if "详细分析" in result:
                    analysis = result["详细分析"]
                    
                    # 数据概览
                    if "数据概况" in result:
                        overview = result["数据概况"]
                        response_parts.append(f"  📈 数据概览: {overview.get('行数', 'N/A')}行数据，{overview.get('列数', 'N/A')}个指标")
                    
                    # 关键指标
                    if "关键指标分析" in analysis:
                        metrics = analysis["关键指标分析"]
                        for metric_name, metric_data in metrics.items():
                            if metric_name == "步数":
                                response_parts.append(f"  👣 平均步数: {metric_data.get('平均值', 'N/A')}")
                            elif metric_name == "运动天数":
                                response_parts.append(f"  🏃 运动频率: {metric_data.get('运动频率', 'N/A')}")
                            elif metric_name == "学习天数":
                                response_parts.append(f"  📚 学习频率: {metric_data.get('学习频率', 'N/A')}")
                    
                    # 模式识别
                    if "模式识别" in analysis and analysis["模式识别"]:
                        response_parts.append(f"  🔍 识别模式: {analysis['模式识别'][0]}")
            
            elif tool_name == "csv_data_validator":
                if "验证结果" in result:
                    validation = result["验证结果"]
                    if "总体评估" in validation:
                        assessment = validation["总体评估"]
                        response_parts.append(f"  ✅ 数据质量: {assessment.get('状态', '未知')}")
            
            elif tool_name == "generate_health_report":
                if "报告" in result:
                    report = result["报告"]
                    if "报告信息" in report:
                        info = report["报告信息"]
                        response_parts.append(f"  📋 报告类型: {info.get('报告类型', '未知')}")
            
            # 添加宪法遵循信息
            if "宪法遵循" in result:
                clauses = result["宪法遵循"]
                if isinstance(clauses, dict):
                    for clause_id, desc in clauses.items():
                        response_parts.append(f"  ⚖️ {clause_id}: {desc}")
            
            response_parts.append("")
        
        # 添加免责声明
        response_parts.append("---")
        response_parts.append("**重要声明**")
        response_parts.append("• 本分析基于提供的数据进行模式识别")
        response_parts.append("• 不构成医疗建议或诊断")
        response_parts.append("• 如有健康问题请咨询专业医疗人员")
        
        return "\n".join(response_parts)

    def _update_context_data_files(self, context: AgentContext):
        """更新上下文数据文件列表"""
        # 获取会话相关的所有数据文件
        session_files = self.data_manager.get_session_data_files(context.session_id)
        context.data_files = list(set(session_files))  # 去重
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话摘要"""
        context = self.get_session(session_id)
        if not context:
            return {"error": "会话不存在"}
        
        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "message_count": len(context.conversation_history),
            "state": context.current_state.value,
            "last_interaction": context.last_interaction.isoformat(),
            "data_files_count": len(context.data_files)
        }
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理旧会话"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        sessions_to_remove = []
        
        for session_id, context in self.sessions.items():
            if context.last_interaction.timestamp() < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            self.logger.info(f"清理了 {len(sessions_to_remove)} 个旧会话")


# 测试函数
def test_orchestrator():
    """测试编排器"""
    import logging
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建编排器
    orchestrator = Orchestrator(use_constitution=True)
    
    # 创建会话
    session_id = orchestrator.create_session()
    print(f" 创建会话: {session_id}")
    
    # 测试查询
    test_queries = [
        "分析我的健康数据",
        "我有头疼症状，请给我诊断",
        "数据显示我的血压正常"
    ]
    
    for query in test_queries:
        print(f"\n 测试查询: {query}")
        print("-" * 50)
        
        result = orchestrator.process_query(session_id, query)
        
        print(f" 成功: {result['success']}")
        print(f" 响应: {result['response'][:100]}...")
        
        if 'constitution_rejected' in result and result['constitution_rejected']:
            print(" 被宪法拒绝")
        elif 'constitution_passed' in result:
            print(f" 宪法检查: {'通过' if result['constitution_passed'] else '未通过'}")
    
    # 获取会话摘要
    summary = orchestrator.get_session_summary(session_id)
    print(f"\n 会话摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_orchestrator()
