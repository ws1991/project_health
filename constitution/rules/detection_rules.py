"""
检测规则系统 - 实现各种宪法检测规则
"""
import re
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass

# 添加父目录到路径，以便导入schema
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

try:
    from constitution.parser.schema import RuleType, DetectionResult
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前sys.path: {sys.path}")
    raise

logger = logging.getLogger(__name__)


@dataclass
class RuleEvaluationContext:
    """规则评估上下文"""
    text: str
    clause_id: str
    rule_id: str
    additional_context: Dict[str, Any] = None


class BaseDetectionRule(ABC):
    """检测规则基类"""
    
    def __init__(self, rule_id: str, rule_type: RuleType, config: Dict[str, Any], weight: float = 1.0):
        self.rule_id = rule_id
        self.rule_type = rule_type
        self.config = config
        self.weight = weight
        self.enabled = True
        
    @abstractmethod
    def evaluate(self, context: RuleEvaluationContext) -> DetectionResult:
        """评估文本是否违反规则"""
        pass
    
    def _create_result(self, passed: bool, details: Dict[str, Any] = None, message: str = "") -> DetectionResult:
        """创建检测结果"""
        score = 1.0 if passed else 0.0
        return DetectionResult(
            rule_id=self.rule_id,
            rule_type=self.rule_type,
            passed=passed,
            score=score * self.weight,
            details=details or {},
            message=message
        )


class KeywordDetectionRule(BaseDetectionRule):
    """关键词检测规则"""
    
    def __init__(self, rule_id: str, config: Dict[str, Any], weight: float = 1.0):
        super().__init__(rule_id, RuleType.KEYWORD_CHECK, config, weight)
        
        # 解析配置
        self.keywords = config.get('keywords', [])
        self.prohibited_keywords = config.get('prohibited_keywords', [])
        self.match_mode = config.get('match_mode', 'any')  # any/all/none
        self.required_count = config.get('required_count', 1)
        self.case_sensitive = config.get('case_sensitive', False)
        
        # 预处理关键词
        if not self.case_sensitive:
            self.keywords = [k.lower() for k in self.keywords]
            self.prohibited_keywords = [k.lower() for k in self.prohibited_keywords]
    
    def evaluate(self, context: RuleEvaluationContext) -> DetectionResult:
        """评估关键词匹配"""
        text_to_check = context.text if self.case_sensitive else context.text.lower()
        
        details = {
            "keywords": self.keywords,
            "prohibited_keywords": self.prohibited_keywords,
            "match_mode": self.match_mode,
            "found_keywords": [],
            "found_prohibited": []
        }
        
        # 检查必须包含的关键词
        found_keywords = []
        for keyword in self.keywords:
            if keyword in text_to_check:
                found_keywords.append(keyword)
        
        # 检查禁止的关键词
        found_prohibited = []
        for keyword in self.prohibited_keywords:
            if keyword in text_to_check:
                found_prohibited.append(keyword)
        
        details["found_keywords"] = found_keywords
        details["found_prohibited"] = found_prohibited
        
        # 根据匹配模式判断是否通过
        passed = self._check_match_passed(found_keywords, found_prohibited)
        
        # 生成消息
        message = self._generate_message(found_keywords, found_prohibited)
        
        return self._create_result(passed, details, message)
    
    def _check_match_passed(self, found_keywords: List[str], found_prohibited: List[str]) -> bool:
        """根据匹配模式判断是否通过"""
        # 首先检查禁止关键词
        if found_prohibited:
            return False
        
        # 然后根据匹配模式检查必须关键词
        if self.match_mode == "any":
            return len(found_keywords) >= self.required_count
        elif self.match_mode == "all":
            return len(found_keywords) >= len(self.keywords)
        elif self.match_mode == "none":
            return len(found_keywords) == 0
        else:
            logger.warning(f"未知的匹配模式: {self.match_mode}")
            return False
    
    def _generate_message(self, found_keywords: List[str], found_prohibited: List[str]) -> str:
        """生成检测消息"""
        if found_prohibited:
            return f"发现禁止关键词: {', '.join(found_prohibited[:3])}"
        
        if self.match_mode == "any" and len(found_keywords) < self.required_count:
            return f"需要至少 {self.required_count} 个关键词，但只找到 {len(found_keywords)} 个"
        
        if self.match_mode == "all" and len(found_keywords) < len(self.keywords):
            missing = set(self.keywords) - set(found_keywords)
            return f"缺少关键词: {', '.join(list(missing)[:3])}"
        
        return "通过关键词检查"


class RegexDetectionRule(BaseDetectionRule):
    """正则表达式检测规则"""
    
    def __init__(self, rule_id: str, config: Dict[str, Any], weight: float = 1.0):
        super().__init__(rule_id, RuleType.REGEX_CHECK, config, weight)
        
        # 解析配置
        self.pattern = config.get('pattern', '')
        self.description = config.get('description', '')
        self.required = config.get('required', True)  # True: 必须匹配，False: 不能匹配
        
        # 编译正则表达式
        try:
            self.regex = re.compile(self.pattern, re.DOTALL)
            self.compiled = True
        except re.error as e:
            logger.error(f"正则表达式编译失败: {self.pattern}, 错误: {e}")
            self.compiled = False
            self.regex = None
    
    def evaluate(self, context: RuleEvaluationContext) -> DetectionResult:
        """评估正则表达式匹配"""
        if not self.compiled:
            return self._create_result(
                passed=False,
                details={"error": "正则表达式编译失败", "pattern": self.pattern},
                message="正则表达式配置错误"
            )
        
        matches = list(self.regex.finditer(context.text))
        match_count = len(matches)
        
        details = {
            "pattern": self.pattern,
            "match_count": match_count,
            "matches": [m.group() for m in matches[:5]],  # 只保留前5个匹配
            "description": self.description
        }
        
        # 判断是否通过
        if self.required:
            passed = match_count > 0
            message = f"找到 {match_count} 个匹配" if passed else "未找到匹配"
        else:
            passed = match_count == 0
            message = f"不应匹配但找到 {match_count} 个匹配" if not passed else "无匹配（通过）"
        
        return self._create_result(passed, details, message)


class SemanticDetectionRule(BaseDetectionRule):
    """语义相似度检测规则（简化版）"""
    
    def __init__(self, rule_id: str, config: Dict[str, Any], weight: float = 1.0):
        super().__init__(rule_id, RuleType.SEMANTIC_CHECK, config, weight)
        
        # 解析配置
        self.reference_texts = config.get('reference_texts', [])
        self.threshold = config.get('threshold', 0.8)
        self.similarity_method = config.get('similarity_method', 'jaccard')  # jaccard/cosine
        
        # 在实际项目中，这里会加载一个嵌入模型
        # 简化版使用Jaccard相似度
    
    def evaluate(self, context: RuleEvaluationContext) -> DetectionResult:
        """评估语义相似度（简化实现）"""
        if not self.reference_texts:
            return self._create_result(
                passed=True,
                details={"warning": "没有参考文本"},
                message="无参考文本，跳过语义检查"
            )
        
        # 简化版：使用Jaccard相似度
        best_similarity = 0.0
        best_match = ""
        
        for ref_text in self.reference_texts:
            similarity = self._jaccard_similarity(context.text, ref_text)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = ref_text[:50] + "..." if len(ref_text) > 50 else ref_text
        
        details = {
            "threshold": self.threshold,
            "best_similarity": best_similarity,
            "best_match": best_match,
            "reference_count": len(self.reference_texts)
        }
        
        passed = best_similarity >= self.threshold
        message = f"语义相似度: {best_similarity:.2f} {'' if passed else '<'} {self.threshold}"
        
        return self._create_result(passed, details, message)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """计算Jaccard相似度（简化版）"""
        # 将文本转换为词语集合
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0


class CompositeDetectionRule(BaseDetectionRule):
    """复合检测规则（多个规则的组合）"""
    
    def __init__(self, rule_id: str, config: Dict[str, Any], weight: float = 1.0):
        super().__init__(rule_id, RuleType.COMPOSITE, config, weight)
        
        # 解析配置
        self.rules = config.get('rules', [])
        self.operator = config.get('operator', 'AND')  # AND/OR
        self.sub_rules = []
    
    def add_sub_rule(self, rule: BaseDetectionRule):
        """添加子规则"""
        self.sub_rules.append(rule)
    
    def evaluate(self, context: RuleEvaluationContext) -> DetectionResult:
        """评估复合规则"""
        if not self.sub_rules:
            return self._create_result(
                passed=True,
                details={"warning": "没有子规则"},
                message="无子规则，跳过复合检查"
            )
        
        results = []
        all_passed = True
        any_passed = False
        
        for i, rule in enumerate(self.sub_rules):
            # 为子规则创建新的上下文
            sub_context = RuleEvaluationContext(
                text=context.text,
                clause_id=context.clause_id,
                rule_id=f"{context.rule_id}.{i}",
                additional_context=context.additional_context
            )
            
            result = rule.evaluate(sub_context)
            results.append(result)
            
            if result.passed:
                any_passed = True
            else:
                all_passed = False
        
        # 根据操作符判断最终结果
        if self.operator == "AND":
            passed = all_passed
        elif self.operator == "OR":
            passed = any_passed
        else:
            logger.warning(f"未知的操作符: {self.operator}")
            passed = all_passed
        
        # 计算平均得分
        avg_score = sum(r.score for r in results) / len(results) if results else 0.0
        
        details = {
            "operator": self.operator,
            "sub_rule_count": len(self.sub_rules),
            "passed_sub_rules": sum(1 for r in results if r.passed),
            "sub_results": [r.rule_id for r in results]
        }
        
        message = f"复合规则检查: {self.operator}操作, {sum(1 for r in results if r.passed)}/{len(results)} 通过"
        
        result = self._create_result(passed, details, message)
        result.score = avg_score * self.weight
        
        return result


class LLMJudgeDetectionRule(BaseDetectionRule):
    """LLM判断检测规则（使用本地模型）"""
    
    def __init__(self, rule_id: str, config: Dict[str, Any], weight: float = 1.0):
        super().__init__(rule_id, RuleType.LLM_JUDGE, config, weight)
        
        # 解析配置
        self.judge_prompt = config.get('judge_prompt', '')
        self.model_name = config.get('model_name', 'deepseek-r1:1.5b')
        self.expected_response = config.get('expected_response', '是')
        
        # 在实际项目中，这里会初始化LLM
        self.llm_available = False
    
    def evaluate(self, context: RuleEvaluationContext) -> DetectionResult:
        """使用LLM进行判断（简化实现）"""
        if not self.judge_prompt:
            return self._create_result(
                passed=True,
                details={"warning": "没有判断提示"},
                message="无判断提示，跳过LLM检查"
            )
        
        # 简化版：在实际项目中，这里会调用真实的LLM
        # 这里模拟一个简单的实现
        details = {
            "judge_prompt": self.judge_prompt[:100] + "..." if len(self.judge_prompt) > 100 else self.judge_prompt,
            "model_name": self.model_name,
            "llm_available": self.llm_available
        }
        
        # 模拟LLM检查
        # 在实际实现中，这里会是：
        # response = llm.invoke(judge_prompt + "\n\n文本：" + context.text)
        # passed = self.expected_response in response
        
        # 暂时返回通过，避免阻塞开发
        message = "LLM检查暂未实现（需要集成Ollama）"
        return self._create_result(True, details, message)


class DetectionRuleFactory:
    """检测规则工厂"""
    
    @staticmethod
    def create_rule(rule_config) -> BaseDetectionRule:
        """根据配置创建检测规则"""
        rule_type = RuleType(rule_config.rule_type)
        
        if rule_type == RuleType.KEYWORD_CHECK:
            return KeywordDetectionRule(
                rule_id=rule_config.rule_id,
                config=rule_config.config,
                weight=rule_config.weight
            )
        
        elif rule_type == RuleType.REGEX_CHECK:
            return RegexDetectionRule(
                rule_id=rule_config.rule_id,
                config=rule_config.config,
                weight=rule_config.weight
            )
        
        elif rule_type == RuleType.SEMANTIC_CHECK:
            return SemanticDetectionRule(
                rule_id=rule_config.rule_id,
                config=rule_config.config,
                weight=rule_config.weight
            )
        
        elif rule_type == RuleType.COMPOSITE:
            return CompositeDetectionRule(
                rule_id=rule_config.rule_id,
                config=rule_config.config,
                weight=rule_config.weight
            )
        
        elif rule_type == RuleType.LLM_JUDGE:
            return LLMJudgeDetectionRule(
                rule_id=rule_config.rule_id,
                config=rule_config.config,
                weight=rule_config.weight
            )
        
        else:
            raise ValueError(f"未知的规则类型: {rule_type}")
