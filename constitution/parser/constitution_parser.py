"""
宪法YAML文件解析器
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .schema import (
    ConstitutionConfig, ConstitutionalClause, ClauseGroup,
    DetectionRuleConfig, EnforcementConfig, ViolationActionConfig,
    EnforcementLevel, RuleType, ViolationAction
)

logger = logging.getLogger(__name__)


class ConstitutionParser:
    """宪法文件解析器"""
    
    def __init__(self, constitution_file: Optional[str] = None):
        self.constitution_file = constitution_file
        self.config: Optional[ConstitutionConfig] = None
        
    def load_from_file(self, file_path: str) -> ConstitutionConfig:
        """从YAML文件加载宪法配置"""
        logger.info(f"加载宪法文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.config = self._parse_config(data)
            logger.info(f"宪法加载成功，版本: {self.config.version}, 条款数: {len(self.config.clauses)}")
            return self.config
            
        except Exception as e:
            logger.error(f"宪法文件解析失败: {e}")
            raise
    
    def load_from_string(self, yaml_content: str) -> ConstitutionConfig:
        """从YAML字符串加载宪法配置"""
        try:
            data = yaml.safe_load(yaml_content)
            self.config = self._parse_config(data)
            return self.config
        except Exception as e:
            logger.error(f"宪法字符串解析失败: {e}")
            raise
    
    def _parse_config(self, data: Dict[str, Any]) -> ConstitutionConfig:
        """解析原始数据为宪法配置对象"""
        
        # 解析条款列表
        clauses = []
        for clause_data in data.get('clauses', []):
            clause = self._parse_clause(clause_data)
            clauses.append(clause)
        
        # 解析条款组
        clause_groups = []
        for group_data in data.get('clause_groups', []):
            group = ClauseGroup(
                name=group_data['name'],
                clause_ids=group_data['clause_ids'],
                description=group_data.get('description', ''),
                enforcement_mode=group_data.get('enforcement_mode', 'strict')
            )
            clause_groups.append(group)
        
        # 构建宪法配置
        config = ConstitutionConfig(
            version=data['version'],
            metadata=data.get('metadata', {}),
            clauses=clauses,
            clause_groups=clause_groups,
            enforcement_config=data.get('enforcement_config', {}),
            audit_config=data.get('audit_config', {})
        )
        
        return config
    
    def _parse_clause(self, clause_data: Dict[str, Any]) -> ConstitutionalClause:
        """解析单个条款"""
        
        # 解析检测规则
        detection_rules = []
        for rule_data in clause_data.get('detection_rules', []):
            rule = DetectionRuleConfig(
                rule_id=rule_data['rule_id'],
                rule_type=RuleType(rule_data['type']),
                config=rule_data.get('config', {}),
                weight=rule_data.get('weight', 1.0),
                enabled=rule_data.get('enabled', True),
                description=rule_data.get('description', '')
            )
            detection_rules.append(rule)
        
        # 解析执行配置
        enforcement_data = clause_data.get('enforcement', {})
        violation_actions = []
        
        for action_data in enforcement_data.get('violation_actions', []):
            action = ViolationActionConfig(
                action=ViolationAction(action_data['action']),
                message=action_data.get('message'),
                tool_name=action_data.get('tool_name'),
                severity=action_data.get('severity', 'medium')
            )
            violation_actions.append(action)
        
        enforcement = EnforcementConfig(
            level=EnforcementLevel(enforcement_data.get('level', 'required')),
            pre_check=enforcement_data.get('pre_check', True),
            post_check=enforcement_data.get('post_check', True),
            violation_actions=violation_actions
        )
        
        # 构建条款对象
        clause = ConstitutionalClause(
            id=clause_data['id'],
            name=clause_data['name'],
            description=clause_data['description'],
            category=clause_data.get('category', 'general'),
            priority=clause_data.get('priority', 100),
            detection_rules=detection_rules,
            enforcement=enforcement,
            associated_tools=clause_data.get('associated_tools', []),
            required_disclaimer=clause_data.get('required_disclaimer'),
            version=clause_data.get('version', '1.0.0'),
            metadata=clause_data.get('metadata', {})
        )
        
        return clause
    
    def get_clause_by_id(self, clause_id: str) -> Optional[ConstitutionalClause]:
        """根据ID获取条款"""
        if not self.config:
            raise ValueError("宪法配置未加载")
        
        for clause in self.config.clauses:
            if clause.id == clause_id:
                return clause
        return None
    
    def get_clauses_by_category(self, category: str) -> List[ConstitutionalClause]:
        """根据分类获取条款"""
        if not self.config:
            raise ValueError("宪法配置未加载")
        
        return [c for c in self.config.clauses if c.category == category]
    
    def get_clauses_with_pre_check(self) -> List[ConstitutionalClause]:
        """获取需要预检查的条款"""
        if not self.config:
            raise ValueError("宪法配置未加载")
        
        return [c for c in self.config.clauses if c.enforcement.pre_check]
    
    def get_clauses_with_post_check(self) -> List[ConstitutionalClause]:
        """获取需要后检查的条款"""
        if not self.config:
            raise ValueError("宪法配置未加载")
        
        return [c for c in self.config.clauses if c.enforcement.post_check]
    
    def validate_config(self) -> List[str]:
        """验证宪法配置的有效性"""
        if not self.config:
            return ["宪法配置未加载"]
        
        errors = []
        
        # 检查条款ID唯一性
        clause_ids = set()
        for clause in self.config.clauses:
            if clause.id in clause_ids:
                errors.append(f"条款ID重复: {clause.id}")
            clause_ids.add(clause.id)
        
        # 检查条款组中的条款是否存在
        for group in self.config.clause_groups:
            for clause_id in group.clause_ids:
                if not self.get_clause_by_id(clause_id):
                    errors.append(f"条款组 '{group.name}' 引用不存在的条款: {clause_id}")
        
        # 检查规则配置
        for clause in self.config.clauses:
            for rule in clause.detection_rules:
                if rule.weight < 0 or rule.weight > 1:
                    errors.append(f"条款 {clause.id} 规则 {rule.rule_id} 权重必须在0-1之间")
        
        return errors
    
    def save_to_file(self, file_path: str, config: Optional[ConstitutionConfig] = None):
        """将宪法配置保存到文件"""
        config_to_save = config or self.config
        if not config_to_save:
            raise ValueError("没有可保存的宪法配置")
        
        # 将配置对象转换为字典
        data = {
            'version': config_to_save.version,
            'metadata': config_to_save.metadata,
            'clauses': [],
            'clause_groups': [],
            'enforcement_config': config_to_save.enforcement_config,
            'audit_config': config_to_save.audit_config
        }
        
        # 转换条款
        for clause in config_to_save.clauses:
            clause_data = {
                'id': clause.id,
                'name': clause.name,
                'description': clause.description,
                'category': clause.category,
                'priority': clause.priority,
                'version': clause.version,
                'detection_rules': [],
                'enforcement': {
                    'level': clause.enforcement.level.value,
                    'pre_check': clause.enforcement.pre_check,
                    'post_check': clause.enforcement.post_check,
                    'violation_actions': []
                },
                'associated_tools': clause.associated_tools,
                'metadata': clause.metadata
            }
            
            if clause.required_disclaimer:
                clause_data['required_disclaimer'] = clause.required_disclaimer
            
            # 转换检测规则
            for rule in clause.detection_rules:
                rule_data = {
                    'rule_id': rule.rule_id,
                    'type': rule.rule_type.value,
                    'config': rule.config,
                    'weight': rule.weight,
                    'enabled': rule.enabled,
                    'description': rule.description
                }
                clause_data['detection_rules'].append(rule_data)
            
            # 转换违规动作
            for action in clause.enforcement.violation_actions:
                action_data = {
                    'action': action.action.value,
                    'severity': action.severity
                }
                if action.message:
                    action_data['message'] = action.message
                if action.tool_name:
                    action_data['tool_name'] = action.tool_name
                clause_data['enforcement']['violation_actions'].append(action_data)
            
            data['clauses'].append(clause_data)
        
        # 转换条款组
        for group in config_to_save.clause_groups:
            group_data = {
                'name': group.name,
                'clause_ids': group.clause_ids,
                'description': group.description,
                'enforcement_mode': group.enforcement_mode
            }
            data['clause_groups'].append(group_data)
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        
        logger.info(f"宪法配置已保存到: $file_path")
