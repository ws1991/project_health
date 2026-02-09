"""
宪法工程化模块入口
"""
from .parser.constitution_parser import ConstitutionParser
from .parser.schema import (
    ConstitutionConfig, ConstitutionalClause, ClauseGroup,
    DetectionRuleConfig, EnforcementConfig, ViolationActionConfig,
    EnforcementLevel, RuleType, ViolationAction,
    ClauseCheckResult, ConstitutionCheckResult
)

__version__ = "0.1.0"
__all__ = [
    'ConstitutionParser',
    'ConstitutionConfig', 'ConstitutionalClause', 'ClauseGroup',
    'DetectionRuleConfig', 'EnforcementConfig', 'ViolationActionConfig',
    'EnforcementLevel', 'RuleType', 'ViolationAction',
    'ClauseCheckResult', 'ConstitutionCheckResult'
]
