# trading_strategies/utils/data_loader.py
import pandas as pd
import numpy as np

class DataLoader:
    """数据加载器"""
    
    @staticmethod
    def load_csv(filepath):
        """从CSV文件加载数据"""
        df = pd.read_csv(filepath)
        
        # 转换日期格式
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
        
        # 确保数值列是正确的类型
        numeric_cols = ['open', 'high', 'low', 'close', 'adjclose', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    @staticmethod
    def prepare_data(df):
        """准备数据用于策略"""
        df = df.copy()
        
        # 确保必要的列存在
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要列: {col}")
        
        return df