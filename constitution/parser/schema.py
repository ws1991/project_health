"""
宪法系统的数据模型定义
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from datetime import datetime


class EnforcementLevel(str, Enum):
    """执行级别枚举"""
    REQUIRED = "required"      # 必须执行，违反则拒绝
    RECOMMENDED = "recommended"  # 建议执行，违反则警告
    OPTIONAL = "optional"      # 可选执行


class RuleType(str, Enum):
    """规则类型枚举"""
    KEYWORD_CHECK = "keyword_check"
    REGEX_CHECK = "regex_check"
    SEMANTIC_CHECK = "semantic_check"
    LLM_JUDGE = "llm_judge"
    COMPOSITE = "composite"


class ViolationAction(str, Enum):
    """违规处理动作"""
    REJECT = "reject"                    # 拒绝执行
    WARN = "warn"                        # 警告但继续
    APPEND_WARNING = "append_warning"    # 添加警告
    SUGGEST_TOOL = "suggest_tool"        # 推荐工具
    LOG_AUDIT = "log_audit"              # 记录审计日志
    CORRECT_AUTO = "correct_auto"        # 自动修正


@dataclass
class DetectionRuleConfig:
    """检测规则配置"""
    rule_id: str
    rule_type: RuleType
    config: Dict[str, Any]  # 具体规则配置
    weight: float = 1.0     # 规则权重
    enabled: bool = True    # 是否启用
    description: str = ""   # 规则描述


@dataclass
class ViolationActionConfig:
    """违规动作配置"""
    action: ViolationAction
    message: Optional[str] = None
    tool_name: Optional[str] = None
    severity: str = "medium"  # low/medium/high


@dataclass
class EnforcementConfig:
    """执行配置"""
    level: EnforcementLevel
    pre_check: bool = True
    post_check: bool = True
    violation_actions: List[ViolationActionConfig] = field(default_factory=list)


@dataclass
class ConstitutionalClause:
    """宪法条款完整定义"""
    id: str                           # 条款ID，如"C-001"
    name: str                        # 条款名称
    description: str                 # 条款描述
    category: str                    # 条款分类
    priority: int = 100              # 优先级
    
    detection_rules: List[DetectionRuleConfig] = field(default_factory=list)
    enforcement: EnforcementConfig = field(default_factory=lambda: EnforcementConfig(
        level=EnforcementLevel.REQUIRED
    ))
    
    # 关联信息
    associated_tools: List[str] = field(default_factory=list)
    required_disclaimer: Optional[str] = None
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClauseGroup:
    """条款组定义"""
    name: str
    clause_ids: List[str]
    description: str = ""
    enforcement_mode: str = "strict"  # strict/lenient/adaptive


@dataclass
class ConstitutionConfig:
    """宪法系统完整配置"""
    version: str
    metadata: Dict[str, Any]
    clauses: List[ConstitutionalClause]
    clause_groups: List[ClauseGroup] = field(default_factory=list)
    
    # 系统级配置
    enforcement_config: Dict[str, Any] = field(default_factory=dict)
    audit_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectionResult:
    """规则检测结果"""
    rule_id: str
    rule_type: RuleType
    passed: bool                     # 是否通过
    score: float = 0.0               # 检测得分（0-1）
    details: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class ClauseCheckResult:
    """条款检查结果"""
    clause_id: str
    clause_name: str
    overall_passed: bool             # 条款整体是否通过
    score: float = 0.0               # 条款得分（加权平均）
    failed_rules: List[str] = field(default_factory=list)  # 失败的规则ID
    passed_rules: List[str] = field(default_factory=list)  # 通过的规则ID
    violation_level: str = "none"    # none/low/medium/high
    suggested_actions: List[ViolationAction] = field(default_factory=list)
    details: List[DetectionResult] = field(default_factory=list)


@dataclass
class ConstitutionCheckResult:
    """宪法检查完整结果"""
    query_id: str                    # 查询ID
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 检查结果
    pre_check: Optional[ClauseCheckResult] = None
    post_check: Optional[ClauseCheckResult] = None
    
    # 总体评估
    overall_passed: bool = True
    overall_score: float = 1.0
    highest_risk_clause: Optional[str] = None
    highest_risk_level: str = "none"
    
    # 执行决策
    should_proceed: bool = True
    requires_correction: bool = False
    correction_suggestions: List[str] = field(default_factory=list)
    
    # 审计信息
    audit_log_id: Optional[str] = None
