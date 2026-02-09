"""
规则评估器 - 执行和管理检测规则
"""
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 添加父目录到路径，以便导入schema
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

try:
    from constitution.parser.schema import (
        ConstitutionalClause, ClauseCheckResult, DetectionResult,
        EnforcementLevel, ViolationAction
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前sys.path: {sys.path}")
    raise

from .detection_rules import (
    BaseDetectionRule, DetectionRuleFactory, RuleEvaluationContext
)

logger = logging.getLogger(__name__)


class RuleEvaluator:
    """规则评估器"""
    
    def __init__(self):
        self.rule_cache: Dict[str, BaseDetectionRule] = {}
    
    def evaluate_clause(self, clause: ConstitutionalClause, text: str, 
                       check_type: str = "pre_check") -> ClauseCheckResult:
        """评估单个条款"""
        
        # 检查是否应该执行此检查
        if check_type == "pre_check" and not clause.enforcement.pre_check:
            return self._create_skipped_result(clause, "跳过预检查")
        if check_type == "post_check" and not clause.enforcement.post_check:
            return self._create_skipped_result(clause, "跳过后检查")
        
        # 获取需要评估的规则
        rules_to_evaluate = []
        for rule_config in clause.detection_rules:
            if rule_config.enabled:
                rule = self._get_or_create_rule(rule_config)
                rules_to_evaluate.append(rule)
        
        if not rules_to_evaluate:
            return self._create_skipped_result(clause, "没有启用的检测规则")
        
        # 评估所有规则
        all_results = []
        failed_rule_ids = []
        passed_rule_ids = []
        total_score = 0.0
        
        for rule in rules_to_evaluate:
            context = RuleEvaluationContext(
                text=text,
                clause_id=clause.id,
                rule_id=rule.rule_id,
                additional_context={"check_type": check_type}
            )
            
            result = rule.evaluate(context)
            all_results.append(result)
            
            if result.passed:
                passed_rule_ids.append(rule.rule_id)
                total_score += result.score
            else:
                failed_rule_ids.append(rule.rule_id)
        
        # 计算整体结果
        rule_count = len(rules_to_evaluate)
        passed_count = len(passed_rule_ids)
        
        # 根据条款的执行级别判断整体是否通过
        if clause.enforcement.level == EnforcementLevel.REQUIRED:
            overall_passed = len(failed_rule_ids) == 0
        elif clause.enforcement.level == EnforcementLevel.RECOMMENDED:
            overall_passed = passed_count >= rule_count * 0.7  # 70%通过即可
        else:  # OPTIONAL
            overall_passed = True
        
        # 计算平均得分
        avg_score = total_score / rule_count if rule_count > 0 else 1.0
        
        # 确定违规级别
        violation_level = self._determine_violation_level(
            clause, failed_rule_ids, rule_count
        )
        
        # 生成建议动作
        suggested_actions = self._get_suggested_actions(clause, overall_passed, violation_level)
        
        # 创建检查结果
        result = ClauseCheckResult(
            clause_id=clause.id,
            clause_name=clause.name,
            overall_passed=overall_passed,
            score=avg_score,
            failed_rules=failed_rule_ids,
            passed_rules=passed_rule_ids,
            violation_level=violation_level,
            suggested_actions=suggested_actions,
            details=all_results
        )
        
        logger.debug(f"条款评估完成: {clause.id}, 通过: {overall_passed}, 得分: {avg_score:.2f}")
        return result
    
    def _get_or_create_rule(self, rule_config) -> BaseDetectionRule:
        """获取或创建检测规则"""
        cache_key = f"{rule_config.rule_id}_{rule_config.rule_type.value}"
        
        if cache_key in self.rule_cache:
            return self.rule_cache[cache_key]
        
        rule = DetectionRuleFactory.create_rule(rule_config)
        self.rule_cache[cache_key] = rule
        return rule
    
    def _create_skipped_result(self, clause: ConstitutionalClause, reason: str) -> ClauseCheckResult:
        """创建跳过检查的结果"""
        return ClauseCheckResult(
            clause_id=clause.id,
            clause_name=clause.name,
            overall_passed=True,
            score=1.0,
            failed_rules=[],
            passed_rules=[],
            violation_level="none",
            suggested_actions=[],
            details=[]
        )
    
    def _determine_violation_level(self, clause: ConstitutionalClause, 
                                  failed_rules: List[str], total_rules: int) -> str:
        """确定违规级别"""
        if not failed_rules:
            return "none"
        
        failure_ratio = len(failed_rules) / total_rules
        
        if clause.enforcement.level == EnforcementLevel.REQUIRED:
            if failure_ratio >= 0.5:
                return "high"
            elif failure_ratio >= 0.3:
                return "medium"
            else:
                return "low"
        
        elif clause.enforcement.level == EnforcementLevel.RECOMMENDED:
            if failure_ratio >= 0.7:
                return "medium"
            else:
                return "low"
        
        else:  # OPTIONAL
            return "low"
    
    def _get_suggested_actions(self, clause: ConstitutionalClause, 
                              overall_passed: bool, violation_level: str) -> List[ViolationAction]:
        """获取建议的动作"""
        if overall_passed:
            return []
        
        # 根据条款配置和违规级别返回建议动作
        suggested_actions = []
        
        for action_config in clause.enforcement.violation_actions:
            # 根据严重程度筛选动作
            severity_mapping = {
                "high": ["reject", "log_audit"],
                "medium": ["warn", "append_warning", "log_audit"],
                "low": ["append_warning", "suggest_tool"]
            }
            
            if action_config.action.value in severity_mapping.get(violation_level, []):
                suggested_actions.append(action_config.action)
        
        return suggested_actions
    
    def batch_evaluate(self, clauses: List[ConstitutionalClause], text: str,
                      check_type: str = "pre_check") -> Dict[str, ClauseCheckResult]:
        """批量评估多个条款"""
        results = {}
        
        for clause in clauses:
            result = self.evaluate_clause(clause, text, check_type)
            results[clause.id] = result
        
        return results
    
    def get_failed_clauses(self, results: Dict[str, ClauseCheckResult]) -> List[str]:
        """获取失败的条款ID"""
        return [clause_id for clause_id, result in results.items() 
                if not result.overall_passed]
    
    def get_high_risk_clauses(self, results: Dict[str, ClauseCheckResult]) -> List[Tuple[str, str]]:
        """获取高风险条款"""
        high_risk = []
        
        for clause_id, result in results.items():
            if result.violation_level in ["high", "medium"]:
                high_risk.append((clause_id, result.violation_level))
        
        # 按优先级排序
        return sorted(high_risk, key=lambda x: x[1], reverse=True)
