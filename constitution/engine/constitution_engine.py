"""
宪法引擎 - 宪法系统的核心执行引擎
"""
import logging
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# 添加父目录到路径
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

try:
    from constitution.parser.constitution_parser import ConstitutionParser
    from constitution.parser.schema import (
        ConstitutionConfig, ConstitutionalClause, ConstitutionCheckResult,
        ClauseCheckResult, EnforcementLevel, ViolationAction
    )
    from constitution.rules.rule_evaluator import RuleEvaluator
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前sys.path: {sys.path}")
    raise

logger = logging.getLogger(__name__)


@dataclass
class EnforcementDecision:
    """执行决策"""
    should_proceed: bool = True
    requires_correction: bool = False
    correction_suggestions: List[str] = None
    safe_response: Optional[str] = None
    warnings: List[str] = None
    audit_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.correction_suggestions is None:
            self.correction_suggestions = []
        if self.warnings is None:
            self.warnings = []
        if self.audit_info is None:
            self.audit_info = {}


class ConstitutionEngine:
    """宪法执行引擎"""
    
    def __init__(self, constitution_file: str = None):
        """初始化宪法引擎"""
        self.parser = ConstitutionParser()
        self.evaluator = RuleEvaluator()
        self.config: Optional[ConstitutionConfig] = None
        
        # 审计日志
        self.audit_logs: List[Dict] = []
        self.query_history: Dict[str, ConstitutionCheckResult] = {}
        
        if constitution_file:
            self.load_constitution(constitution_file)
    
    def load_constitution(self, constitution_file: str) -> ConstitutionConfig:
        """加载宪法文件"""
        self.config = self.parser.load_from_file(constitution_file)
        logger.info(f"宪法引擎初始化完成，版本: {self.config.version}")
        return self.config
    
    def check_input(self, user_input: str, query_id: str = None):
        """检查用户输入（预检查）"""
        if not self.config:
            raise ValueError("宪法配置未加载")
        
        query_id = query_id or str(uuid.uuid4())[:8]
        
        # 获取需要预检查的条款
        pre_check_clauses = self.parser.get_clauses_with_pre_check()
        
        # 执行预检查
        pre_check_results = self.evaluator.batch_evaluate(
            pre_check_clauses, user_input, "pre_check"
        )
        
        # 分析预检查结果
        pre_check_summary = self._summarize_check_results(pre_check_results, "pre_check")
        
        # 生成执行决策
        enforcement_decision = self._make_enforcement_decision(
            pre_check_results, user_input
        )
        
        # 创建检查结果
        result = ConstitutionCheckResult(
            query_id=query_id,
            pre_check=pre_check_summary,
            overall_passed=enforcement_decision.should_proceed,
            overall_score=pre_check_summary.score,
            highest_risk_clause=self._get_highest_risk_clause(pre_check_results),
            highest_risk_level=pre_check_summary.violation_level,
            should_proceed=enforcement_decision.should_proceed,
            requires_correction=enforcement_decision.requires_correction,
            correction_suggestions=enforcement_decision.correction_suggestions or []
        )
        
        # 记录审计日志
        self._log_audit(query_id, "pre_check", user_input, result, enforcement_decision)
        
        # 保存到历史
        self.query_history[query_id] = result
        
        return result, enforcement_decision
    
    def check_output(self, ai_output: str, query_id: str) -> ConstitutionCheckResult:
        """检查AI输出（后检查）"""
        if not self.config:
            raise ValueError("宪法配置未加载")
        
        if query_id not in self.query_history:
            raise ValueError(f"查询ID不存在: {query_id}")
        
        # 获取需要后检查的条款
        post_check_clauses = self.parser.get_clauses_with_post_check()
        
        # 执行后检查
        post_check_results = self.evaluator.batch_evaluate(
            post_check_clauses, ai_output, "post_check"
        )
        
        # 分析后检查结果
        post_check_summary = self._summarize_check_results(post_check_results, "post_check")
        
        # 获取之前的预检查结果
        previous_result = self.query_history[query_id]
        
        # 创建完整的检查结果
        result = ConstitutionCheckResult(
            query_id=query_id,
            pre_check=previous_result.pre_check,
            post_check=post_check_summary,
            overall_passed=post_check_summary.overall_passed,
            overall_score=(previous_result.overall_score + post_check_summary.score) / 2,
            highest_risk_clause=self._get_highest_risk_clause(post_check_results),
            highest_risk_level=post_check_summary.violation_level,
            should_proceed=True,  # 输出后总是继续（但可能修正）
            requires_correction=not post_check_summary.overall_passed,
            correction_suggestions=self._generate_corrections(post_check_results, ai_output)
        )
        
        # 更新历史记录
        self.query_history[query_id] = result
        
        # 记录审计日志
        self._log_audit(query_id, "post_check", ai_output, result, None)
        
        return result
    
    def apply_constitutional_corrections(self, text: str, check_result: ConstitutionCheckResult) -> str:
        """应用宪法修正"""
        if not check_result.requires_correction:
            return text
        
        corrected_text = text
        
        # 1. 添加安全声明
        if check_result.post_check and hasattr(check_result.post_check, 'details_by_clause'):
            for clause_id, clause_result in check_result.post_check.details_by_clause.items():
                clause = self.parser.get_clause_by_id(clause_id)
                if clause and clause.required_disclaimer:
                    if not clause.required_disclaimer in corrected_text:
                        corrected_text += f"\n\n{clause.required_disclaimer}"
        
        # 2. 修正高风险内容
        high_risk_clauses = self.evaluator.get_high_risk_clauses(
            check_result.post_check.details_by_clause if check_result.post_check and hasattr(check_result.post_check, 'details_by_clause') else {}
        )
        
        for clause_id, _ in high_risk_clauses:
            clause = self.parser.get_clause_by_id(clause_id)
            if clause and clause.enforcement.level == EnforcementLevel.REQUIRED:
                # 这里可以添加更复杂的修正逻辑
                corrected_text = self._apply_clause_corrections(corrected_text, clause)
        
        return corrected_text
    
    def _summarize_check_results(self, results: Dict[str, ClauseCheckResult], 
                                check_type: str) -> ClauseCheckResult:
        """汇总检查结果"""
        if not results:
            return ClauseCheckResult(
                clause_id=f"summary_{check_type}",
                clause_name=f"{check_type}汇总",
                overall_passed=True,
                score=1.0,
                violation_level="none"
            )
        
        # 计算总体通过率
        passed_clauses = [r for r in results.values() if r.overall_passed]
        overall_passed = len(passed_clauses) == len(results)
        
        # 计算平均得分
        total_score = sum(r.score for r in results.values())
        avg_score = total_score / len(results)
        
        # 确定最高风险级别
        violation_levels = [r.violation_level for r in results.values()]
        highest_risk = "none"
        for level in ["high", "medium", "low"]:
            if level in violation_levels:
                highest_risk = level
                break
        
        # 创建结果对象
        result = ClauseCheckResult(
            clause_id=f"summary_{check_type}",
            clause_name=f"{check_type}汇总",
            overall_passed=overall_passed,
            score=avg_score,
            violation_level=highest_risk
        )
        
        # 添加详细结果
        setattr(result, 'details_by_clause', results)
        
        return result
    
    def _make_enforcement_decision(self, results: Dict[str, ClauseCheckResult], 
                                  user_input: str) -> EnforcementDecision:
        """根据检查结果做出执行决策"""
        decision = EnforcementDecision()
        
        # 检查是否有必须拒绝的情况
        for clause_id, result in results.items():
            if not result.overall_passed:
                clause = self.parser.get_clause_by_id(clause_id)
                if clause and clause.enforcement.level == EnforcementLevel.REQUIRED:
                    # 检查是否需要拒绝
                    for action in result.suggested_actions:
                        if action == ViolationAction.REJECT:
                            decision.should_proceed = False
                            decision.safe_response = self._generate_safe_response(clause, user_input)
                            decision.audit_info = {
                                "rejected_clause": clause_id,
                                "violation_level": result.violation_level,
                                "reason": "违反必须遵守的宪法条款"
                            }
                            return decision
        
        # 检查是否需要修正或警告
        high_risk_clauses = self.evaluator.get_high_risk_clauses(results)
        
        if high_risk_clauses:
            decision.requires_correction = True
            
            for clause_id, risk_level in high_risk_clauses:
                clause = self.parser.get_clause_by_id(clause_id)
                if clause:
                    # 生成修正建议
                    suggestions = self._generate_clause_suggestions(clause, risk_level)
                    decision.correction_suggestions.extend(suggestions)
                    
                    # 添加警告
                    if risk_level in ["high", "medium"]:
                        warning = f"注意: {clause.name} 风险级别: {risk_level}"
                        decision.warnings.append(warning)
        
        return decision
    
    def _get_highest_risk_clause(self, results: Dict[str, ClauseCheckResult]) -> Optional[str]:
        """获取最高风险的条款"""
        high_risk = self.evaluator.get_high_risk_clauses(results)
        return high_risk[0][0] if high_risk else None
    
    def _generate_safe_response(self, clause: ConstitutionalClause, user_input: str) -> str:
        """生成安全响应"""
        # 获取拒绝消息
        rejection_msg = ""
        for action in clause.enforcement.violation_actions:
            if action.action == ViolationAction.REJECT and action.message:
                rejection_msg = action.message
                break
        
        if not rejection_msg:
            rejection_msg = f"抱歉，根据'{clause.name}'，我无法处理这个请求。"
        
        # 添加安全建议
        if clause.associated_tools:
            tools_str = "、".join(clause.associated_tools)
            rejection_msg += f"\n\n您可以尝试使用以下工具: {tools_str}"
        
        return rejection_msg
    
    def _generate_clause_suggestions(self, clause: ConstitutionalClause, risk_level: str) -> List[str]:
        """为条款生成修正建议"""
        suggestions = []
        
        # 基础建议
        base_suggestion = f"优化'{clause.name}'相关的内容"
        suggestions.append(base_suggestion)
        
        # 工具建议
        if clause.associated_tools:
            tools_str = "、".join(clause.associated_tools[:3])
            suggestions.append(f"考虑使用工具: {tools_str}")
        
        # 根据风险级别添加特定建议
        if risk_level == "high":
            suggestions.append("建议彻底修改相关内容")
        elif risk_level == "medium":
            suggestions.append("建议添加澄清说明")
        
        return suggestions
    
    def _generate_corrections(self, results: Dict[str, ClauseCheckResult], text: str) -> List[str]:
        """生成修正建议"""
        corrections = []
        
        for clause_id, result in results.items():
            if not result.overall_passed:
                clause = self.parser.get_clause_by_id(clause_id)
                if clause:
                    # 从失败的规则中提取具体问题
                    for detail in result.details:
                        if not detail.passed and detail.message:
                            correction = f"【{clause.name}】{detail.message}"
                            corrections.append(correction)
        
        # 去重
        return list(set(corrections))
    
    def _apply_clause_corrections(self, text: str, clause: ConstitutionalClause) -> str:
        """应用条款特定的修正"""
        # 这里可以实现更复杂的修正逻辑
        # 目前只是简单的示例
        
        corrected_text = text
        
        # 示例：为安全条款添加免责声明
        if clause.category == "safety" and clause.required_disclaimer:
            if clause.required_disclaimer not in corrected_text:
                corrected_text += f"\n\n{clause.required_disclaimer}"
        
        return corrected_text
    
    def _log_audit(self, query_id: str, check_type: str, text: str, 
                  result: ConstitutionCheckResult, decision: Optional[EnforcementDecision]):
        """记录审计日志"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id,
            "check_type": check_type,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "overall_passed": result.overall_passed,
            "overall_score": result.overall_score,
            "highest_risk_clause": result.highest_risk_clause,
            "highest_risk_level": result.highest_risk_level,
            "should_proceed": result.should_proceed,
            "requires_correction": result.requires_correction,
            "decision_info": decision.audit_info if decision else None
        }
        
        self.audit_logs.append(audit_entry)
        logger.info(f"审计日志: {check_type}检查, 查询ID: {query_id}, 通过: {result.overall_passed}")
    
    def get_audit_summary(self, limit: int = 10) -> List[Dict]:
        """获取审计摘要"""
        return self.audit_logs[-limit:] if self.audit_logs else []
    
    def get_constitution_stats(self) -> Dict[str, Any]:
        """获取宪法统计信息"""
        if not self.config:
            return {}
        
        stats = {
            "version": self.config.version,
            "clause_count": len(self.config.clauses),
            "categories": {},
            "enforcement_levels": {},
            "recent_checks": len(self.audit_logs),
            "success_rate": 0.0
        }
        
        # 按类别统计
        for clause in self.config.clauses:
            category = clause.category
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            level = clause.enforcement.level.value
            stats["enforcement_levels"][level] = stats["enforcement_levels"].get(level, 0) + 1
        
        # 计算成功率
        if self.audit_logs:
            successful = sum(1 for log in self.audit_logs if log["overall_passed"])
            stats["success_rate"] = successful / len(self.audit_logs)
        
        return stats
    
    def validate_constitution(self) -> Tuple[bool, List[str]]:
        """验证宪法配置"""
        if not self.config:
            return False, ["宪法配置未加载"]
        
        errors = self.parser.validate_config()
        return len(errors) == 0, errors
