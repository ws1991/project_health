"""
AI客户端 - 管理本地Ollama连接
"""
import os
from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOllama


class HybridAIClient:
    def __init__(self, config: Dict):
        self.config = config
        self.mode = config.get('ai', {}).get('mode', 'local')
        self.local_config = config.get('ai', {}).get('local', {})
        
        print(f"🤖 AI客户端初始化 - 模式: {self.mode}")
    
    def get_client_for_task(self, task_type: str = "default") -> ChatOllama:
        """获取AI客户端"""
        # 根据任务类型选择模型（简化版）
        model = self.local_config.get('model', 'deepseek-r1:1.5b')
        
        if task_type in ["report_generation", "complex_analysis"]:
            # 复杂任务可使用更大模型
            if "qwen3:8b" in self._get_available_models():
                model = "qwen3:8b"
        
        print(f"   使用模型: {model} ({task_type})")
        
        return ChatOllama(
            base_url=self.local_config.get('base_url', 'http://localhost:11434'),
            model=model,
            temperature=self.local_config.get('temperature', 0.1),
            timeout=30
        )
    
    def _get_available_models(self) -> list:
        """获取可用的本地模型"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model['name'] for model in response.json()['models']]
                return models
        except:
            pass
        return []
    
    def get_client(self) -> ChatOllama:
        """获取默认客户端"""
        return self.get_client_for_task("default")