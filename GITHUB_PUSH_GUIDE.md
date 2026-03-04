# AlphaFabric - GitHub 推送指南

## 快速开始

### 方法一：使用自动化脚本（推荐）

```bash
# 1. 进入 AlphaFabric 目录
cd AlphaFabric

# 2. 给脚本执行权限
chmod +x init_github.sh

# 3. 运行脚本
./init_github.sh
```

### 方法二：手动推送

#### 步骤 1：初始化 Git 仓库

```bash
cd AlphaFabric

# 初始化 git
git init

# 配置用户信息（如未配置）
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### 步骤 2：添加并提交代码

```bash
# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: AlphaFabric AI量化交易系统"
```

#### 步骤 3：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `AlphaFabric`
   - **Description**: `AI量化交易系统 - 支持A股全市场数据`
   - **Visibility**: Public（或 Private）
3. 点击 **Create repository**

#### 步骤 4：推送代码

```bash
# 添加远程仓库
git remote add origin https://github.com/georgetang19810616-dot/AlphaFabric.git

# 推送代码
git branch -M main
git push -u origin main
```

## 使用 GitHub CLI（推荐）

### 安装 GitHub CLI

**macOS:**
```bash
brew install gh
```

**Windows:**
```bash
winget install --id GitHub.cli
```

**Linux:**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 登录 GitHub CLI

```bash
gh auth login
```

### 创建并推送仓库

```bash
# 进入项目目录
cd AlphaFabric

# 初始化 git
git init
git add .
git commit -m "Initial commit"

# 创建 GitHub 仓库并推送
gh repo create AlphaFabric \
  --public \
  --description "AI量化交易系统 - 支持A股全市场数据" \
  --source=. \
  --remote=origin \
  --push
```

## 配置 GitHub Secrets（用于 KIMI CLAW 部署）

### 添加 TUSHARE_TOKEN

1. 访问仓库页面: https://github.com/georgetang19810616-dot/AlphaFabric
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写：
   - **Name**: `TUSHARE_TOKEN`
   - **Secret**: 你的 TUSHARE PRO TOKEN
5. 点击 **Add secret**

### 添加 KIMI CLAW 配置

```bash
# 添加其他 secrets
gh secret set TUSHARE_TOKEN --body "your_token_here"
```

## 常见问题

### Q1: 推送失败，提示 "Permission denied"

**解决方案：**

1. 配置 SSH 密钥：
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 添加密钥到 ssh-agent
ssh-add ~/.ssh/id_ed25519

# 复制公钥
cat ~/.ssh/id_ed25519.pub
```

2. 在 GitHub 添加 SSH 密钥：
   - 访问 https://github.com/settings/keys
   - 点击 **New SSH key**
   - 粘贴公钥内容

3. 使用 SSH 方式推送：
```bash
git remote set-url origin git@github.com:georgetang19810616-dot/AlphaFabric.git
git push
```

### Q2: 推送失败，提示 "rejected: non-fast-forward"

**解决方案：**

```bash
# 先拉取远程代码
git pull origin main --rebase

# 再推送
git push
```

### Q3: 大文件推送失败

**解决方案：**

```bash
# 安装 Git LFS
git lfs install

# 追踪大文件
git lfs track "*.onnx"
git lfs track "*.h5"

# 提交并推送
git add .gitattributes
git commit -m "Add Git LFS"
git push
```

### Q4: 如何更新代码

```bash
# 修改代码后
git add .
git commit -m "Update: xxx"
git push
```

## 仓库设置建议

### 启用 GitHub Actions（可选）

创建 `.github/workflows/ci.yml`：

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
```

### 添加 README 徽章

在 README.md 顶部添加：

```markdown
# AlphaFabric

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![KIMI CLAW](https://img.shields.io/badge/Deploy-KIMI%20CLAW-orange.svg)](https://kimi-claw.moonshot.cn)

AI量化交易系统 - 支持A股全市场数据
```

## 相关链接

- GitHub 仓库: https://github.com/georgetang19810616-dot/AlphaFabric
- KIMI CLAW: https://kimi-claw.moonshot.cn
- TUSHARE PRO: https://tushare.pro

## 下一步

推送完成后，你可以：

1. **部署到 KIMI CLAW**: 参考 [KIMI_CLAW_DEPLOY.md](./KIMI_CLAW_DEPLOY.md)
2. **配置 GitHub Actions**: 实现自动化测试和部署
3. **邀请协作者**: 在仓库 Settings 中添加合作者
