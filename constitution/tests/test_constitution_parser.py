"""
宪法解析器测试 - 修复版
"""
import unittest
import tempfile
import os
from pathlib import Path

# 导入解析器
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from constitution.parser.constitution_parser import ConstitutionParser
from constitution.parser.schema import EnforcementLevel, RuleType


class TestConstitutionParser(unittest.TestCase):
    """宪法解析器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = ConstitutionParser()
        
        # 创建测试YAML内容
        self.test_yaml = """version: "2.0.0"
metadata:
  name: "测试宪法"
  author: "测试员"

clauses:
  - id: "C-001"
    name: "测试条款"
    description: "这是一个测试条款"
    category: "test"
    priority: 100
    
    detection_rules:
      - rule_id: "R-001-001"
        type: "keyword_check"
        config:
          keywords: ["测试", "检查"]
          match_mode: "any"
        weight: 1.0
    
    enforcement:
      level: "required"
      pre_check: true
      post_check: true
      violation_actions:
        - action: "reject"
          message: "测试拒绝"
    
    associated_tools: ["test_tool"]
    
clause_groups:
  - name: "测试组"
    clause_ids: ["C-001"]
    description: "测试条款组"

enforcement_config:
  default_mode: "adaptive"

audit_config:
  enabled: true"""
    
    def test_load_from_string(self):
        """测试从字符串加载"""
        config = self.parser.load_from_string(self.test_yaml)
        
        self.assertEqual(config.version, "2.0.0")
        self.assertEqual(len(config.clauses), 1)
        self.assertEqual(config.clauses[0].id, "C-001")
        self.assertEqual(config.clauses[0].enforcement.level, EnforcementLevel.REQUIRED)
    
    def test_load_from_file(self):
        """测试从文件加载"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(self.test_yaml)
            temp_file = f.name
        
        try:
            config = self.parser.load_from_file(temp_file)
            self.assertEqual(config.version, "2.0.0")
            self.assertEqual(len(config.clauses), 1)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_get_clause_by_id(self):
        """测试根据ID获取条款"""
        self.parser.load_from_string(self.test_yaml)
        
        clause = self.parser.get_clause_by_id("C-001")
        self.assertIsNotNone(clause)
        self.assertEqual(clause.name, "测试条款")
        
        clause = self.parser.get_clause_by_id("C-999")
        self.assertIsNone(clause)
    
    def test_get_clauses_by_category(self):
        """测试根据分类获取条款"""
        self.parser.load_from_string(self.test_yaml)
        
        clauses = self.parser.get_clauses_by_category("test")
        self.assertEqual(len(clauses), 1)
        self.assertEqual(clauses[0].id, "C-001")
        
        clauses = self.parser.get_clauses_by_category("nonexistent")
        self.assertEqual(len(clauses), 0)
    
    def test_validate_config(self):
        """测试配置验证"""
        self.parser.load_from_string(self.test_yaml)
        
        errors = self.parser.validate_config()
        self.assertEqual(len(errors), 0)
        
        # 测试无效配置
        invalid_yaml = """version: "1.0.0"
metadata: {}
clauses:
  - id: "C-001"
    name: "条款1"
    description: "描述"
    category: "test"
    priority: 100
    detection_rules:
      - rule_id: "R-001"
        type: "keyword_check"
        config: {}
        weight: 2.0"""
        
        parser2 = ConstitutionParser()
        parser2.load_from_string(invalid_yaml)
        errors = parser2.validate_config()
        self.assertGreater(len(errors), 0)
    
    def test_save_to_file(self):
        """测试保存到文件"""
        self.parser.load_from_string(self.test_yaml)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            temp_file = f.name
        
        try:
            self.parser.save_to_file(temp_file)
            
            # 重新加载验证
            parser2 = ConstitutionParser()
            config2 = parser2.load_from_file(temp_file)
            self.assertEqual(config2.version, "2.0.0")
            self.assertEqual(len(config2.clauses), 1)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
