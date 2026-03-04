# AlphaFabric - AI量化交易系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![KIMI CLAW](https://img.shields.io/badge/Deploy-KIMI%20CLAW-orange.svg)](https://kimi-claw.moonshot.cn)

针对2核4GB服务器优化的轻量级A股量化交易系统，支持**全市场A股数据**。

> **GitHub 仓库**: https://github.com/georgetang19810616-dot/AlphaFabric

## 系统特性

- **数据层**：TUSHARE PRO数据接入，支持A股全市场5000+只股票，SQLite本地缓存
- **策略层**：5个核心策略（双均线、MACD、动量、价值、AI预测）
- **因子层**：30个核心因子（估值/质量/动量/波动/技术/资金/情绪）
- **AI决策**：2个轻量模型（LSTM+XGBoost）投票决策
- **回测模块**：完整的回测引擎与绩效分析
- **风险控制**：仓位限制、止损止盈、最大回撤控制
- **交易接口**：模拟交易 + 券商API支持

## 股票池配置

支持灵活配置股票池范围：

```yaml
# config/config.yaml
data:
  # 股票池选项: "all"=全市场A股, "hs300"=沪深300
  stock_pool: "all"
  # 全市场数据时，限制处理股票数量（低配服务器建议设置100-500）
  max_stocks: 500
```

## 低配服务器优化

| 优化项 | 措施 | 效果 |
|--------|------|------|
| 数据范围 | 可配置股票数量上限 | 灵活控制 |
| 策略数量 | 15个 → 5个核心策略 | 减少66%计算 |
| 因子数量 | 100+ → 30个核心因子 | 减少70%计算 |
| AI模型 | 5个 → 2个轻量模型 | 内存降低60% |
| 执行方式 | 并行 → 串行 | 避免进程开销 |
| 缓存方案 | Redis → SQLite | 减少内存占用 |

## 推送到 GitHub

```bash
# 1. 运行自动化脚本
chmod +x init_github.sh
./init_github.sh

# 或手动推送
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/georgetang19810616-dot/AlphaFabric.git
git push -u origin main
```

详细说明请参考 [GITHUB_PUSH_GUIDE.md](./GITHUB_PUSH_GUIDE.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置TUSHARE TOKEN

编辑 `config/config.yaml`：

```yaml
tushare:
  token: "your_tushare_token_here"
```

获取TOKEN：[TUSHARE PRO](https://tushare.pro/register)

### 3. 运行测试

```bash
# 测试数据模块
python -m pytest tests/test_data.py -v

# 测试策略
python -m pytest tests/test_strategies.py -v

# 测试回测
python -m pytest tests/test_backtest.py -v
```

### 4. 运行选股

```bash
python run.py --mode select
```

### 5. 运行回测

```bash
python run.py --mode backtest --strategy double_ma
```

### 6. 模拟交易

```bash
python run.py --mode trade
```

## KIMI CLAW 部署（推荐）

AlphaFabric 已针对 KIMI CLAW 云平台优化，支持一键部署。

### 快速部署

```bash
# 1. 安装 KIMI CLAW CLI
pip install kimi-claw

# 2. 登录
kimi-claw login

# 3. 配置 TUSHARE TOKEN
export TUSHARE_TOKEN=your_token_here

# 4. 部署
kimi-claw deploy -f kimi-claw.yaml
```

### 查看状态

```bash
# 查看应用状态
kimi-claw status alphafabric

# 查看日志
kimi-claw logs alphafabric -f
```

详细部署说明请参考 [KIMI_CLAW_DEPLOY.md](./KIMI_CLAW_DEPLOY.md)

## Docker部署

```bash
# 构建镜像
docker build -t alphafabric .

# 运行容器
docker run -d \
  -e TUSHARE_TOKEN=your_token \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --memory=3.5g \
  --cpus=2.0 \
  alphafabric
```

或使用 Docker Compose:

```bash
docker-compose up -d
```

## 项目结构

```
AlphaFabric/
├── config/
│   └── config.yaml          # 配置文件
├── data/                    # 数据目录
├── data_source/             # 数据源模块（支持全市场A股）
├── strategies/              # 策略模块
├── factors/                 # 因子模块
├── ai/                      # AI决策模块
├── backtest/                # 回测模块
├── risk/                    # 风控模块
├── trading/                 # 交易接口
├── utils/                   # 工具函数
├── tests/                   # 测试用例
├── requirements.txt         # 依赖列表
├── run.py                   # 主程序
├── web_server.py            # Web服务（KIMI CLAW健康检查）
├── Dockerfile               # Docker镜像
├── docker-compose.yml       # Docker编排
├── kimi-claw.yaml           # KIMI CLAW部署配置
├── KIMI_CLAW_DEPLOY.md      # KIMI CLAW部署指南
└── README.md               # 说明文档
```

## 核心策略

1. **双均线策略**：金叉买入，死叉卖出
2. **MACD策略**：DIF上穿DEA买入
3. **动量策略**：选择近期涨幅居前的股票
4. **价值策略**：选择低估值股票
5. **AI预测策略**：LSTM预测涨跌

## 绩效指标

回测完成后输出以下指标：

- 总收益率
- 年化收益
- 最大回撤
- 夏普比率
- 波动率
- 胜率
- 盈亏比

## 风险提示

**本系统仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。**

## License

MIT License
