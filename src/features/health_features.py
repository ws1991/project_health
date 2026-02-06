"""健康相关特征工程"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class HealthFeatureEngineer:
    """健康特征工程师"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def create_health_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建所有健康相关特征"""
        df_features = df.copy()
        
        # 1. 癫痫发作特征
        if 'seizure' in df_features.columns:
            df_features = self._create_seizure_features(df_features)
        
        # 2. 锻炼特征
        if 'exercise' in df_features.columns:
            df_features = self._create_exercise_features(df_features)
        
        # 3. 步数特征
        if 'step' in df_features.columns:
            df_features = self._create_step_features(df_features)
        
        # 4. 综合健康评分
        df_features = self._create_health_score(df_features)
        
        return df_features
    
    def _create_seizure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建癫痫发作相关特征"""
        # 发作严重程度分类
        thresholds = self.config.get('thresholds', {}).get('seizure', {})
        
        conditions = [
            df['seizure'] == thresholds.get('none', 0),
            df['seizure'] == thresholds.get('mild', 1),
            df['seizure'] == thresholds.get('moderate', 2),
            df['seizure'] >= thresholds.get('severe', 3)
        ]
        choices = ['无发作', '轻微', '中度', '严重']
        
        df['seizure_severity'] = np.select(conditions, choices, default='未知')
        
        # 发作频率特征
        if len(df) > 1:
            # 标记是否有发作
            df['had_seizure'] = (df['seizure'] > 0).astype(int)
            
            # 连续无发作天数
            df['seizure_free_days'] = df['had_seizure'].eq(0).groupby(
                df['had_seizure'].ne(df['had_seizure'].shift()).cumsum()
            ).cumsum()
            
            # 发作强度变化
            df['seizure_change'] = df['seizure'].diff()
        
        # 创建发作模式特征
        if 'date' in df.columns and len(df) >= 7:
            # 7天内发作次数
            df['seizure_count_7d'] = df['seizure'].rolling(window=7, min_periods=1).apply(
                lambda x: (x > 0).sum()
            )
            
            # 7天内平均发作强度
            df['seizure_intensity_7d'] = df['seizure'].rolling(window=7, min_periods=1).mean()
        
        return df
    
    def _create_exercise_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建锻炼相关特征"""
        # 锻炼强度分类
        thresholds = self.config.get('thresholds', {}).get('exercise', {})
        
        conditions = [
            df['exercise'] == thresholds.get('none', 0),
            df['exercise'] == thresholds.get('light', 1),
            df['exercise'] == thresholds.get('moderate', 2),
            df['exercise'] >= thresholds.get('intense', 3)
        ]
        choices = ['无锻炼', '轻度', '中度', '高强度']
        
        df['exercise_intensity'] = np.select(conditions, choices, default='未知')
        
        # 锻炼频率特征
        if len(df) > 1:
            # 是否锻炼
            df['did_exercise'] = (df['exercise'] > 0).astype(int)
            
            # 连续锻炼天数
            df['exercise_streak'] = df['did_exercise'].groupby(
                df['did_exercise'].ne(df['did_exercise'].shift()).cumsum()
            ).cumsum() * df['did_exercise']
        
        # 与步数的相关性特征
        if 'step' in df.columns:
            df['total_activity'] = df['step'] * 0.1 + df['exercise'] * 1000
        
        return df
    
    def _create_step_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建步数相关特征"""
        # 活动水平分类
        thresholds = self.config.get('thresholds', {}).get('activity', {})
        
        conditions = [
            df['step'] < thresholds.get('sedentary', 3000),
            df['step'] < thresholds.get('moderate', 5000),
            df['step'] < thresholds.get('active', 7500),
            df['step'] >= thresholds.get('active', 7500)
        ]
        choices = ['久坐', '轻度活动', '中等活动', '非常活跃']
        
        df['activity_level'] = np.select(conditions, choices, default='未知')
        
        # 步数变化特征
        if len(df) > 1:
            df['step_change'] = df['step'].diff()
            df['step_change_pct'] = df['step'].pct_change() * 100
        
        # 活动量评分
        def step_score(steps):
            if pd.isna(steps):
                return np.nan
            if steps < 3000:
                return 1
            elif steps < 5000:
                return 2
            elif steps < 7500:
                return 3
            elif steps < 10000:
                return 4
            else:
                return 5
        
        df['step_score'] = df['step'].apply(step_score)
        
        return df
    
    def _create_health_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建综合健康评分"""
        # 初始化评分
        df['health_score'] = 50  # 基准分
        
        # 1. 睡眠质量贡献
        if 'sleep_duration_score' in df.columns:
            df['health_score'] += df['sleep_duration_score'] * 5
        
        # 2. 活动量贡献
        if 'step_score' in df.columns:
            df['health_score'] += df['step_score'] * 3
        
        # 3. 锻炼贡献
        if 'exercise' in df.columns:
            df['health_score'] += df['exercise'] * 5
        
        # 4. 癫痫发作扣分
        if 'seizure' in df.columns:
            df['health_score'] -= df['seizure'] * 10
        
        # 确保评分在合理范围
        df['health_score'] = df['health_score'].clip(0, 100)
        
        # 健康状态分类
        conditions = [
            df['health_score'] >= 80,
            df['health_score'] >= 60,
            df['health_score'] >= 40,
            df['health_score'] < 40
        ]
        choices = ['优秀', '良好', '一般', '需改善']
        
        df['health_status'] = np.select(conditions, choices, default='未知')
        
        return df