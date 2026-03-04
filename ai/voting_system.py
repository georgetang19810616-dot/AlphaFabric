"""轻量AI投票决策系统"""
import os
import logging
import numpy as np
import pandas as pd
from typing import List, Dict

logger = logging.getLogger('AlphaFabric')


class LiteLSTMExpert:
    """轻量LSTM专家"""
    
    def __init__(self, model_path: str = None):
        self.name = "LSTM_Lite"
        self.model_path = model_path or "./ai/models/lstm_lite.onnx"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载ONNX模型"""
        try:
            import onnxruntime as ort
            if os.path.exists(self.model_path):
                self.model = ort.InferenceSession(self.model_path)
                logger.info(f"加载LSTM模型成功: {self.model_path}")
            else:
                logger.warning(f"模型文件不存在: {self.model_path}")
        except Exception as e:
            logger.error(f"加载LSTM模型失败: {e}")
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """准备特征"""
        # 使用最近20天的价格数据
        close = data['close'].values[-20:]
        
        # 归一化
        if close.std() > 0:
            close_norm = (close - close.mean()) / close.std()
        else:
            close_norm = close - close.mean()
        
        # 填充到固定长度
        if len(close_norm) < 20:
            close_norm = np.pad(close_norm, (20 - len(close_norm), 0), mode='edge')
        
        return close_norm.reshape(1, 20, 1).astype(np.float32)
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """预测涨跌概率"""
        if self.model is None:
            # 使用简单规则
            scores = []
            for _, row in features.iterrows():
                # 基于动量简单预测
                momentum = row.get('Momentum_1M', 0)
                score = 0.5 + momentum * 5  # 映射到0-1
                score = np.clip(score, 0, 1)
                scores.append(score)
            return np.array(scores)
        
        try:
            predictions = []
            for _, row in features.iterrows():
                # 提取特征
                feat = row[['Momentum_1M', 'Momentum_3M', 'RSI_14', 'MACD', 'MA5', 'MA20', 'Volatility']].values
                feat = feat.reshape(1, -1).astype(np.float32)
                
                pred = self.model.run(None, {'input': feat})[0][0][0]
                predictions.append(pred)
            
            return np.array(predictions)
        except Exception as e:
            logger.error(f"LSTM预测失败: {e}")
            return np.ones(len(features)) * 0.5


class LiteXGBoostExpert:
    """轻量XGBoost专家"""
    
    def __init__(self, model_path: str = None):
        self.name = "XGBoost"
        self.model_path = model_path or "./ai/models/xgb_lite.json"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载XGBoost模型"""
        try:
            import xgboost as xgb
            if os.path.exists(self.model_path):
                self.model = xgb.Booster()
                self.model.load_model(self.model_path)
                logger.info(f"加载XGBoost模型成功: {self.model_path}")
            else:
                logger.warning(f"模型文件不存在: {self.model_path}")
        except Exception as e:
            logger.error(f"加载XGBoost模型失败: {e}")
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """预测涨跌概率"""
        if self.model is None:
            # 使用简单规则
            scores = []
            for _, row in features.iterrows():
                # 综合多个因子
                score = 0.5
                score += row.get('Momentum_1M', 0) * 3
                score += row.get('ROE', 0) * 2
                score -= row.get('Volatility', 0) * 0.5
                score = np.clip(score, 0, 1)
                scores.append(score)
            return np.array(scores)
        
        try:
            import xgboost as xgb
            dmatrix = xgb.DMatrix(features)
            predictions = self.model.predict(dmatrix)
            return predictions
        except Exception as e:
            logger.error(f"XGBoost预测失败: {e}")
            return np.ones(len(features)) * 0.5


class LiteAIVotingSystem:
    """轻量AI投票决策系统"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.experts = []
        self.weights = []
        self._init_experts()
    
    def _init_experts(self):
        """初始化专家"""
        models_config = self.config.get('models', [
            {'name': 'lstm_lite', 'path': './ai/models/lstm_lite.onnx', 'weight': 0.6},
            {'name': 'xgboost', 'path': './ai/models/xgb_lite.json', 'weight': 0.4}
        ])
        
        for model_cfg in models_config:
            name = model_cfg['name']
            path = model_cfg['path']
            weight = model_cfg['weight']
            
            if name == 'lstm_lite':
                expert = LiteLSTMExpert(path)
            elif name == 'xgboost':
                expert = LiteXGBoostExpert(path)
            else:
                continue
            
            self.experts.append(expert)
            self.weights.append(weight)
        
        logger.info(f"初始化AI投票系统: {len(self.experts)}个专家")
    
    def vote(self, stock_features: pd.DataFrame) -> List[str]:
        """专家投票选出Top N"""
        if len(stock_features) == 0:
            return []
        
        # 归一化权重
        weights = np.array(self.weights)
        weights = weights / weights.sum()
        
        # 各专家投票
        votes = np.zeros(len(stock_features))
        
        for expert, weight in zip(self.experts, weights):
            try:
                scores = expert.predict(stock_features)
                votes += scores * weight
            except Exception as e:
                logger.error(f"{expert.name}预测失败: {e}")
        
        # 添加到DataFrame
        stock_features = stock_features.copy()
        stock_features['ai_score'] = votes
        
        # 选出Top N
        top_n = self.config.get('top_n', 10)
        top_stocks = stock_features.nlargest(top_n, 'ai_score')
        
        logger.info(f"AI投票选出Top {top_n}: {top_stocks['code'].tolist()}")
        return top_stocks['code'].tolist()
    
    def get_scores(self, stock_features: pd.DataFrame) -> pd.DataFrame:
        """获取各股票的AI评分"""
        if len(stock_features) == 0:
            return stock_features
        
        weights = np.array(self.weights)
        weights = weights / weights.sum()
        
        votes = np.zeros(len(stock_features))
        
        for expert, weight in zip(self.experts, weights):
            try:
                scores = expert.predict(stock_features)
                votes += scores * weight
            except Exception as e:
                logger.error(f"{expert.name}预测失败: {e}")
        
        stock_features = stock_features.copy()
        stock_features['ai_score'] = votes
        
        return stock_features
