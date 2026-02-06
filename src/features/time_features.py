"""时间相关特征工程"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class TimeFeatureEngineer:
    """时间特征工程师"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建所有时间相关特征"""
        df_features = df.copy()
        
        # 1. 睡眠时间特征
        if 'sleep_duration_hours' in df_features.columns:
            df_features = self._create_sleep_duration_features(df_features)
        
        # 2. 作息规律性特征
        if 'bedtime_hour' in df_features.columns:
            df_features = self._create_regularity_features(df_features)
        
        # 3. 时间序列特征
        if 'date' in df_features.columns:
            df_features = self._create_temporal_features(df_features)
        
        return df_features
    
    def _create_sleep_duration_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建睡眠时长相关特征"""
        # 睡眠时长分类
        thresholds = self.config.get('thresholds', {}).get('sleep', {})
        short_thresh = thresholds.get('short_sleep', 7)
        long_thresh = thresholds.get('long_sleep', 9)
        optimal_thresh = thresholds.get('optimal_sleep', 7.5)
        
        conditions = [
            df['sleep_duration_hours'] < short_thresh,
            df['sleep_duration_hours'] >= short_thresh,
            df['sleep_duration_hours'] > long_thresh
        ]
        choices = ['睡眠不足', '睡眠正常', '睡眠过长']
        
        df['sleep_duration_category'] = np.select(conditions, choices, default='未知')
        
        # 睡眠质量评分（基于时长）
        def sleep_duration_score(duration):
            if pd.isna(duration):
                return np.nan
            if duration < 6:
                return 1
            elif duration < 7:
                return 2
            elif duration < 8:
                return 3
            elif duration <= 9:
                return 4
            else:
                return 3
        
        df['sleep_duration_score'] = df['sleep_duration_hours'].apply(sleep_duration_score)
        
        # 连续睡眠时长变化
        if len(df) > 1:
            df['sleep_duration_change'] = df['sleep_duration_hours'].diff()
            df['sleep_duration_change_pct'] = df['sleep_duration_hours'].pct_change() * 100
        
        return df
    
    def _create_regularity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建作息规律性特征"""
        # 计算就寝时间标准差（最近7天）
        if len(df) >= 7:
            df['bedtime_std_7d'] = df['bedtime_hour'].rolling(window=7, min_periods=1).std()
            df['wakeup_std_7d'] = df['wakeup_hour'].rolling(window=7, min_periods=1).std()
        
        # 计算作息时间差
        df['bedtime_variation'] = df['bedtime_hour'].diff().abs()
        df['wakeup_variation'] = df['wakeup_hour'].diff().abs()
        
        # 标记作息是否规律
        if 'bedtime_std_7d' in df.columns:
            df['is_regular_sleep'] = df['bedtime_std_7d'].apply(
                lambda x: 1 if x < 1.5 else 0  # 标准差小于1.5小时视为规律
            )
        
        return df
    
    def _create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建时间序列特征"""
        # 按日期排序
        df = df.sort_values('date').reset_index(drop=True)
        
        # 移动平均和标准差
        windows = [3, 7, 14]  # 3天, 1周, 2周
        
        for window in windows:
            # 睡眠时长移动平均
            if 'sleep_duration_hours' in df.columns:
                df[f'sleep_duration_ma_{window}d'] = df['sleep_duration_hours'].rolling(
                    window=window, min_periods=1
                ).mean()
            
            # 步数移动平均
            if 'step' in df.columns:
                df[f'steps_ma_{window}d'] = df['step'].rolling(
                    window=window, min_periods=1
                ).mean()
        
        # 周内位置特征
        df['day_of_week_num'] = df['date'].dt.dayofweek
        df['is_monday'] = (df['day_of_week_num'] == 0).astype(int)
        df['is_friday'] = (df['day_of_week_num'] == 4).astype(int)
        
        # 季节性特征
        df['month_sin'] = np.sin(2 * np.pi * df['date'].dt.month / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['date'].dt.month / 12)
        
        # 周内天数
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week_num'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week_num'] / 7)
        
        return df