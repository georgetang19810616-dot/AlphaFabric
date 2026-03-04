#!/usr/bin/env python3
"""
AlphaFabric - AI量化交易系统
针对2核4GB服务器优化，支持A股全市场数据
"""
import os
import sys
import argparse
import logging
import time
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import load_config, setup_logging
from data_source import LiteTushareDataSource
from strategies import (
    DoubleMAStrategy, MACDStrategy, MomentumStrategy,
    ValueStrategy, LiteAIPredictStrategy
)
from factors import FactorEngine
from ai import LiteAIVotingSystem
from backtest import LiteBacktestEngine, BacktestConfig
from trading import SimulatedTrader

# Web服务器（用于KIMI CLAW健康检查）
try:
    from web_server import start_web_server, update_status
    WEB_SERVER_AVAILABLE = True
except ImportError:
    WEB_SERVER_AVAILABLE = False


def init_system(config_path: str = "./config/config.yaml"):
    """初始化系统"""
    # 加载配置
    config = load_config(config_path)
    
    # 设置日志
    logger = setup_logging(config)
    logger.info("=" * 60)
    logger.info("  AlphaFabric - AI量化交易系统")
    logger.info("  支持A股全市场数据 | 针对低配服务器优化")
    logger.info("=" * 60)
    
    return config


def get_stock_pool(data_source: LiteTushareDataSource, config: dict) -> list:
    """根据配置获取股票池"""
    stock_pool_config = config['data'].get('stock_pool', 'all')
    max_stocks = config['data'].get('max_stocks', 0)
    
    if stock_pool_config == 'all':
        stocks = data_source.get_all_stocks()
        logger = logging.getLogger('AlphaFabric')
        logger.info(f"股票池: 全市场A股 ({len(stocks)}只)")
    elif stock_pool_config == 'hs300':
        stocks = data_source.get_hs300_stocks()
        logger = logging.getLogger('AlphaFabric')
        logger.info(f"股票池: 沪深300 ({len(stocks)}只)")
    else:
        stocks = data_source.get_all_stocks()
        logger = logging.getLogger('AlphaFabric')
        logger.info(f"股票池: 默认全市场 ({len(stocks)}只)")
    
    # 限制股票数量（低配服务器优化）
    if max_stocks > 0 and len(stocks) > max_stocks:
        stocks = stocks[:max_stocks]
        logger = logging.getLogger('AlphaFabric')
        logger.info(f"限制处理股票数量: {max_stocks}只")
    
    return stocks


def run_data_update(config: dict):
    """更新数据"""
    logger = logging.getLogger('AlphaFabric')
    logger.info("开始更新数据...")
    
    token = config['tushare']['token']
    if not token:
        logger.error("请配置TUSHARE TOKEN")
        return
    
    data_source = LiteTushareDataSource(
        token=token,
        cache_path=config['data']['cache_path']
    )
    
    # 获取股票池
    stocks = get_stock_pool(data_source, config)
    logger.info(f"待更新股票数量: {len(stocks)}")
    
    # 更新数据
    for i, code in enumerate(stocks):
        if i % 50 == 0:
            logger.info(f"数据更新进度: {i}/{len(stocks)}")
        data_source.get_daily_data(code, days=config['data']['history_days'])
    
    logger.info("数据更新完成")


def run_strategy_scan(config: dict):
    """运行策略扫描"""
    logger = logging.getLogger('AlphaFabric')
    logger.info("开始策略扫描...")
    
    token = config['tushare']['token']
    if not token:
        logger.error("请配置TUSHARE TOKEN")
        return []
    
    # 初始化数据源
    data_source = LiteTushareDataSource(
        token=token,
        cache_path=config['data']['cache_path']
    )
    
    # 获取股票池
    stocks = get_stock_pool(data_source, config)
    logger.info(f"扫描股票数量: {len(stocks)}")
    
    # 加载数据
    stock_data = {}
    for i, code in enumerate(stocks):
        if i % 100 == 0:
            logger.info(f"数据加载进度: {i}/{len(stocks)}")
        df = data_source.get_daily_data(code, days=100)
        if df is not None and len(df) > 30:
            stock_data[code] = df
    
    logger.info(f"成功加载数据: {len(stock_data)}只")
    
    # 初始化策略
    strategies = []
    if 'double_ma' in config['strategies']['enabled']:
        strategies.append(DoubleMAStrategy(config['strategies'].get('double_ma', {})))
    if 'macd' in config['strategies']['enabled']:
        strategies.append(MACDStrategy(config['strategies'].get('macd', {})))
    if 'momentum' in config['strategies']['enabled']:
        strategies.append(MomentumStrategy(config['strategies'].get('momentum', {})))
    if 'value' in config['strategies']['enabled']:
        strategies.append(ValueStrategy(config['strategies'].get('value', {})))
    if 'ai_predict' in config['strategies']['enabled']:
        strategies.append(LiteAIPredictStrategy(config['strategies'].get('ai_predict', {})))
    
    logger.info(f"启用策略数量: {len(strategies)}")
    
    # 执行策略
    all_signals = []
    for strategy in strategies:
        logger.info(f"执行策略: {strategy.name}")
        signals = strategy.run(stock_data)
        all_signals.extend(signals)
        logger.info(f"  生成信号: {len(signals)}个")
    
    # 统计买入信号
    buy_signals = [s for s in all_signals if s.action == 'buy']
    logger.info(f"总买入信号: {len(buy_signals)}个")
    
    return buy_signals


def run_factor_scoring(config: dict, stock_codes: list = None):
    """运行因子评分"""
    logger = logging.getLogger('AlphaFabric')
    logger.info("开始因子评分...")
    
    token = config['tushare']['token']
    data_source = LiteTushareDataSource(
        token=token,
        cache_path=config['data']['cache_path']
    )
    
    # 获取股票池
    if stock_codes is None:
        stock_codes = get_stock_pool(data_source, config)
    
    # 加载数据
    stock_data = {}
    for i, code in enumerate(stock_codes):
        if i % 100 == 0:
            logger.info(f"因子数据加载进度: {i}/{len(stock_codes)}")
        df = data_source.get_daily_data(code, days=150)
        if df is not None and len(df) > 60:
            stock_data[code] = df
    
    # 计算因子
    factor_engine = FactorEngine()
    scores = factor_engine.calculate_batch(stock_data)
    
    logger.info(f"因子评分完成: {len(scores)}只股票")
    
    return scores


def run_ai_voting(config: dict, factor_scores: dict = None):
    """运行AI投票决策"""
    logger = logging.getLogger('AlphaFabric')
    logger.info("开始AI投票决策...")
    
    # 如果没有因子数据，先计算
    if factor_scores is None or len(factor_scores) == 0:
        factor_scores = run_factor_scoring(config)
    
    if len(factor_scores) == 0:
        logger.warning("没有可用的因子数据")
        return []
    
    # AI投票
    ai_system = LiteAIVotingSystem(config.get('ai', {}))
    top_stocks = ai_system.vote(factor_scores)
    
    logger.info(f"AlphaFabric AI投票选出Top {len(top_stocks)}")
    
    return top_stocks


def run_backtest(config: dict, strategy_name: str = 'double_ma'):
    """运行回测"""
    logger = logging.getLogger('AlphaFabric')
    logger.info(f"开始回测策略: {strategy_name}")
    
    token = config['tushare']['token']
    if not token:
        logger.error("请配置TUSHARE TOKEN")
        return None
    
    # 回测配置
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    backtest_config = BacktestConfig(
        token=token,
        start_date=start_date.strftime('%Y%m%d'),
        end_date=end_date.strftime('%Y%m%d'),
        initial_capital=config['backtest']['initial_capital'],
        commission_rate=config['backtest']['commission_rate'],
        slippage=config['backtest']['slippage']
    )
    
    # 初始化回测引擎
    engine = LiteBacktestEngine(backtest_config)
    
    # 设置策略
    if strategy_name == 'double_ma':
        strategy = DoubleMAStrategy(config['strategies'].get('double_ma', {}))
    elif strategy_name == 'macd':
        strategy = MACDStrategy(config['strategies'].get('macd', {}))
    else:
        strategy = DoubleMAStrategy()
    
    engine.set_strategy(strategy)
    
    # 执行回测
    results = engine.run()
    
    # 打印报告
    report = engine.generate_report()
    print(report)
    
    return results


def run_paper_trading(config: dict):
    """运行模拟交易"""
    logger = logging.getLogger('AlphaFabric')
    logger.info("开始模拟交易...")
    
    # 初始化模拟交易
    trader = SimulatedTrader(config['trading'].get('simulated', {}))
    trader.connect()
    
    # 选股流程
    logger.info("步骤1: 策略扫描")
    signals = run_strategy_scan(config)
    
    logger.info("步骤2: 因子评分")
    factor_scores = run_factor_scoring(config, [s.code for s in signals])
    
    logger.info("步骤3: AI投票")
    top_stocks = run_ai_voting(config, factor_scores)
    
    # 执行交易
    logger.info("步骤4: 执行交易")
    for code in top_stocks[:5]:  # 只买前5只
        # 获取最新价格
        token = config['tushare']['token']
        data_source = LiteTushareDataSource(token, config['data']['cache_path'])
        df = data_source.get_daily_data(code, days=5)
        
        if df is not None and len(df) > 0:
            price = df['close'].iloc[-1]
            quantity = min(100, int(trader.cash * 0.1 / price))  # 每只最多10%资金
            if quantity > 0:
                trader.buy(code, price, quantity)
    
    # 打印持仓
    summary = trader.get_portfolio_summary()
    logger.info(f"模拟交易完成: {summary}")
    
    return trader


def run_daemon_mode(config: dict):
    """守护模式运行（用于KIMI CLAW持续运行）"""
    logger = logging.getLogger('AlphaFabric')
    logger.info("启动守护模式...")
    
    # 启动Web服务器
    if WEB_SERVER_AVAILABLE:
        web_port = int(os.getenv('PORT', '8000'))
        start_web_server(web_port)
        logger.info(f"Web服务器已启动，端口: {web_port}")
    
    # 主循环
    while True:
        try:
            now = datetime.now()
            
            # 工作日15:30执行选股
            if now.weekday() < 5 and now.hour == 15 and now.minute == 30:
                logger.info("定时任务: 执行每日选股")
                signals = run_strategy_scan(config)
                factor_scores = run_factor_scoring(config, [s.code for s in signals])
                top_stocks = run_ai_voting(config, factor_scores)
                
                # 更新状态
                update_status(
                    last_select=now.isoformat(),
                    top_stocks=top_stocks
                )
                
                logger.info(f"选股完成: {top_stocks}")
                
                # 等待1分钟避免重复执行
                time.sleep(60)
            
            # 每5分钟更新一次状态
            if now.minute % 5 == 0:
                update_status(timestamp=now.isoformat())
            
            time.sleep(30)  # 30秒检查一次
            
        except Exception as e:
            logger.error(f"守护模式异常: {e}")
            time.sleep(60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AlphaFabric - AI量化交易系统')
    parser.add_argument('--mode', type=str, default='select',
                        choices=['select', 'backtest', 'trade', 'update', 'daemon'],
                        help='运行模式: select=选股, backtest=回测, trade=模拟交易, update=更新数据, daemon=守护模式')
    parser.add_argument('--config', type=str, default='./config/config.yaml',
                        help='配置文件路径')
    parser.add_argument('--strategy', type=str, default='double_ma',
                        help='回测策略名称')
    
    args = parser.parse_args()
    
    # 初始化系统
    config = init_system(args.config)
    
    # 检查TOKEN
    token = config['tushare']['token']
    if not token:
        print("错误: 请在config/config.yaml中配置TUSHARE TOKEN")
        print("获取TOKEN: https://tushare.pro/register")
        return 1
    
    # 执行对应模式
    if args.mode == 'update':
        run_data_update(config)
    
    elif args.mode == 'select':
        # 选股流程
        signals = run_strategy_scan(config)
        factor_scores = run_factor_scoring(config, [s.code for s in signals])
        top_stocks = run_ai_voting(config, factor_scores)
        
        print("\n" + "=" * 50)
        print("选股结果")
        print("=" * 50)
        for i, code in enumerate(top_stocks, 1):
            print(f"{i}. {code}")
        print("=" * 50)
    
    elif args.mode == 'backtest':
        run_backtest(config, args.strategy)
    
    elif args.mode == 'trade':
        run_paper_trading(config)
    
    elif args.mode == 'daemon':
        # 守护模式（KIMI CLAW推荐）
        run_daemon_mode(config)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
