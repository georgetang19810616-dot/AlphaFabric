# AlphaFabric - KIMI CLAW 部署指南

## 简介

本文档介绍如何通过 KIMI CLAW 部署 AlphaFabric 量化交易系统。

## 前置条件

1. 注册 [KIMI CLAW](https://kimi-claw.moonshot.cn) 账号
2. 获取 [TUSHARE PRO](https://tushare.pro/register) TOKEN
3. 准备 Docker 环境（可选）

## 部署方式

### 方式一：通过 KIMI CLAW Web 控制台部署（推荐）

#### 步骤 1：准备代码

```bash
# 克隆或下载 AlphaFabric 代码
git clone https://github.com/yourname/alphafabric.git
cd alphafabric

# 确保包含以下文件
# - kimi-claw.yaml
# - Dockerfile
# - run.py
# - web_server.py
```

#### 步骤 2：配置环境变量

编辑 `kimi-claw.yaml` 文件，设置 TUSHARE TOKEN：

```yaml
env:
  - name: TUSHARE_TOKEN
    value: "your_tushare_token_here"  # 替换为你的TOKEN
```

#### 步骤 3：登录 KIMI CLAW

```bash
# 安装 KIMI CLAW CLI（如未安装）
pip install kimi-claw

# 登录
kimi-claw login
```

#### 步骤 4：部署应用

```bash
# 使用配置文件部署
kimi-claw deploy -f kimi-claw.yaml

# 或使用目录部署
kimi-claw deploy .
```

#### 步骤 5：查看部署状态

```bash
# 查看应用状态
kimi-claw status alphafabric

# 查看日志
kimi-claw logs alphafabric -f
```

### 方式二：通过 Docker 镜像部署

#### 步骤 1：构建镜像

```bash
# 构建 Docker 镜像
docker build -t alphafabric:latest .

# 标记镜像（替换为你的仓库地址）
docker tag alphafabric:latest registry.kimi-claw.cn/yourname/alphafabric:latest

# 推送镜像
docker push registry.kimi-claw.cn/yourname/alphafabric:latest
```

#### 步骤 2：在 KIMI CLAW 控制台创建应用

1. 登录 [KIMI CLAW 控制台](https://kimi-claw.moonshot.cn)
2. 点击「创建应用」
3. 选择「从镜像部署」
4. 填写镜像地址：`registry.kimi-claw.cn/yourname/alphafabric:latest`
5. 配置环境变量：
   - `TUSHARE_TOKEN`: 你的 TUSHARE TOKEN
6. 配置资源：2核CPU，4GB内存
7. 点击「部署」

### 方式三：通过 Git 仓库自动部署

#### 步骤 1：推送代码到 Git 仓库

```bash
git add .
git commit -m "Initial AlphaFabric deployment"
git push origin main
```

#### 步骤 2：在 KIMI CLAW 配置自动部署

1. 登录 [KIMI CLAW 控制台](https://kimi-claw.moonshot.cn)
2. 点击「创建应用」
3. 选择「从 Git 仓库部署」
4. 授权并选择你的 Git 仓库
5. 配置构建命令：
   ```bash
   pip install -r requirements.txt
   ```
6. 配置启动命令：
   ```bash
   python run.py --mode daemon
   ```
7. 配置环境变量
8. 点击「部署」

## 配置文件说明

### kimi-claw.yaml

```yaml
apiVersion: v1
kind: Deployment
metadata:
  name: alphafabric
  
# 资源配置
resources:
  cpu: 2          # CPU核心数
  memory: 4Gi     # 内存大小
  disk: 20Gi      # 磁盘大小

# 环境变量
env:
  - name: TUSHARE_TOKEN
    value: ""     # 必填：TUSHARE TOKEN

# 定时任务
cronjobs:
  - name: daily-select
    schedule: "35 15 * * 1-5"  # 工作日15:35执行选股
    command: "python run.py --mode select"
```

### 关键配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `TUSHARE_TOKEN` | TUSHARE PRO API Token | 必填 |
| `ALPHAFABRIC_MODE` | 运行模式 | daemon |
| `ALPHAFABRIC_LOG_LEVEL` | 日志级别 | INFO |
| `max_stocks` | 处理股票数量上限 | 500 |

## 健康检查

AlphaFabric 提供以下健康检查端点：

- `GET /health` - 健康状态检查
- `GET /status` - 系统状态查询
- `GET /metrics` - Prometheus 格式指标

KIMI CLAW 会自动调用 `/health` 端点进行健康检查。

## 定时任务

系统预置以下定时任务：

| 任务名称 | 执行时间 | 说明 |
|----------|----------|------|
| daily-update | 15:30 | 每日数据更新 |
| daily-select | 15:35 | 每日选股 |
| weekly-cleanup | 周日 02:00 | 数据清理 |

## 监控告警

### 内置监控指标

- `cpu_usage` - CPU使用率
- `memory_usage` - 内存使用率
- `disk_usage` - 磁盘使用率
- `stock_count` - 已缓存股票数量
- `last_select_time` - 上次选股时间

### 告警规则

- **高内存告警**: 内存使用率 > 85%
- **磁盘满告警**: 磁盘使用率 > 90%
- **数据过期告警**: 超过1天未更新数据

## 日志查看

```bash
# 查看实时日志
kimi-claw logs alphafabric -f

# 查看最近100行日志
kimi-claw logs alphafabric --tail 100

# 查看特定时间段的日志
kimi-claw logs alphafabric --since 1h
```

## 常见问题

### Q1: 部署失败，提示 "TUSHARE_TOKEN not set"

**解决方案**: 确保在环境变量中正确设置了 TUSHARE_TOKEN

```bash
kimi-claw config set alphafabric TUSHARE_TOKEN=your_token
```

### Q2: 内存不足导致 OOM

**解决方案**: 
1. 减少 `max_stocks` 配置值
2. 增加内存资源限制
3. 优化数据处理逻辑

### Q3: 数据更新失败

**解决方案**:
1. 检查 TUSHARE TOKEN 是否有效
2. 检查网络连接
3. 查看日志排查具体错误

### Q4: 如何手动执行选股

```bash
# 进入容器
kimi-claw exec alphafabric -- /bin/bash

# 执行选股
python run.py --mode select
```

## 更新部署

```bash
# 更新代码后重新部署
kimi-claw deploy -f kimi-claw.yaml

# 或仅更新环境变量
kimi-claw config set alphafabric TUSHARE_TOKEN=new_token
```

## 删除部署

```bash
kimi-claw delete alphafabric
```

## 参考文档

- [KIMI CLAW 官方文档](https://kimi-claw.moonshot.cn/docs)
- [TUSHARE PRO API](https://tushare.pro/document/2)
- [AlphaFabric 项目文档](./README.md)

## 技术支持

如有问题，请联系：
- KIMI CLAW 支持: support@kimi-claw.moonshot.cn
- AlphaFabric 项目: https://github.com/yourname/alphafabric
