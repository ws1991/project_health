"""增强版数据加载器 - 处理多时间字段"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re
from datetime import datetime, timedelta
import logging
import yaml

logger = logging.getLogger(__name__)


"""增强版数据加载器 - 处理多时间字段"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re
from datetime import datetime, timedelta
import logging
import yaml

logger = logging.getLogger(__name__)


class EnhancedDataLoader:
    """增强版数据加载器，专门处理时间字段"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self._setup_logging()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_and_parse_data(self, filepath: str = None) -> pd.DataFrame:
        """
        加载并解析数据，特别处理时间字段
        
        Args:
            filepath: 数据文件路径，如果为None则使用配置中的路径
            
        Returns:
            解析后的DataFrame
        """
        # 使用配置文件中的路径或提供的路径
        if filepath is None:
            filepath = f"data/raw/{self.config['data']['raw_file']}"
        
        logger.info(f"加载数据: {filepath}")
        
        # 加载原始数据
        df = self._load_file(filepath)
        
        # 解析时间字段
        df = self._parse_time_columns(df)
        
        # 计算衍生特征
        df = self._calculate_features(df)
        
        logger.info(f"数据加载完成，形状: {df.shape}")
        return df
    
    def _load_file(self, filepath: str) -> pd.DataFrame:
        """加载文件"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        # 根据扩展名选择读取方式
        if filepath.suffix == '.csv':
            df = pd.read_csv(filepath, encoding='utf-8')
        elif filepath.suffix == '.xlsx':
            df = pd.read_excel(filepath)
        elif filepath.suffix == '.json':
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"不支持的文件格式: {filepath.suffix}")
        
        return df
        
    def _parse_time_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """解析时间相关的列"""
        config = self.config['data']
        
        # 1. 解析日期列
        date_col = config['columns']['date']
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(
                df[date_col], 
                format=config['time_formats']['date_format'],
                errors='coerce'
            )
        
        # 2. 解析睡眠时间
        sleep_col = config['columns']['sleep_time']
        if sleep_col in df.columns:
            df['sleep_datetime'] = self._parse_datetime_column(
                df[sleep_col], 
                config['time_formats']['datetime_format']
            )
        
        # 3. 解析起床时间
        wake_col = config['columns']['wake_time']
        if wake_col in df.columns:
            df['wake_datetime'] = self._parse_datetime_column(
                df[wake_col], 
                config['time_formats']['datetime_format']
            )
        
        # 4. 解析备注中的关键词
        if 'note' in df.columns:
            df = self._extract_note_keywords(df)
        
        return df
    
    def _parse_datetime_column(self, series: pd.Series, format_str: str) -> pd.Series:
        """
        解析包含时区的日期时间字符串
        
        Args:
            series: 包含日期时间字符串的序列
            format_str: 日期时间格式
            
        Returns:
            解析后的datetime序列
        """
        def parse_datetime_with_timezone(val):
            if pd.isna(val):
                return pd.NaT
            
            # 移除时区信息
            if isinstance(val, str):
                # 提取日期时间部分
                match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日 \d{1,2}:\d{2})', val)
                if match:
                    datetime_str = match.group(1)
                    try:
                        return datetime.strptime(datetime_str, format_str)
                    except:
                        return pd.NaT
            return pd.NaT
        
        return series.apply(parse_datetime_with_timezone)
    
    def _extract_note_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """从备注中提取关键词"""
        # 定义关键词分类
        sleep_keywords = {
            '噩梦': ['噩梦', '噩梦', 'bad dream'],
            '良好': ['良好', 'good', '睡得好'],
            '不足': ['不足', '不够', '不足'],
            '超时': ['超时', '过长', 'oversleep'],
            '锻炼': ['锻炼', '运动', 'exercise', 'workout']
        }
        
        def extract_keywords(note):
            if pd.isna(note):
                return []
            
            keywords = []
            note_lower = str(note).lower()
            
            for category, words in sleep_keywords.items():
                for word in words:
                    if word in note_lower:
                        keywords.append(category)
                        break
            
            return keywords
        
        df['note_keywords'] = df['note'].apply(extract_keywords)
        
        # 创建二值特征
        for category in sleep_keywords.keys():
            df[f'has_{category}'] = df['note_keywords'].apply(
                lambda x: 1 if category in x else 0
            )
        
        return df
    
    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算衍生特征"""
        # 1. 计算睡眠时长（小时）
        if 'sleep_datetime' in df.columns and 'wake_datetime' in df.columns:
            # 处理跨夜情况
            df['sleep_duration_hours'] = df.apply(
                lambda row: self._calculate_sleep_duration(
                    row['sleep_datetime'], 
                    row['wake_datetime']
                ), 
                axis=1
            )
        
        # 2. 计算就寝时间（小时）
        if 'sleep_datetime' in df.columns:
            df['bedtime_hour'] = df['sleep_datetime'].dt.hour + df['sleep_datetime'].dt.minute / 60
            
            # 分类：早睡(<22), 正常(22-0), 晚睡(>0)
            df['bedtime_category'] = pd.cut(
                df['bedtime_hour'],
                bins=[0, 22, 24, 25],
                labels=['早睡', '正常', '晚睡'],
                include_lowest=True
            )
        
        # 3. 计算起床时间
        if 'wake_datetime' in df.columns:
            df['wakeup_hour'] = df['wake_datetime'].dt.hour + df['wake_datetime'].dt.minute / 60
        
        # 4. 计算睡眠效率（如果可能）
        # 这里可以添加更复杂的睡眠效率计算
        
        # 5. 创建日期特征
        if 'date' in df.columns:
            df['day_of_week'] = df['date'].dt.day_name()
            df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
        
        return df
    
    def _calculate_sleep_duration(self, sleep_time, wake_time) -> float:
        """计算睡眠时长，处理跨夜情况"""
        if pd.isna(sleep_time) or pd.isna(wake_time):
            return np.nan
        
        # 确保唤醒时间在睡眠时间之后
        if wake_time < sleep_time:
            # 假设跨夜，为唤醒时间加上一天
            wake_time += timedelta(days=1)
        
        duration = (wake_time - sleep_time).total_seconds() / 3600
        return round(duration, 2)