#!/bin/bash
# AlphaFabric - GitHub 仓库初始化脚本
# 使用方法: ./init_github.sh

set -e

# 配置信息
GITHUB_USER="georgetang19810616-dot"
REPO_NAME="AlphaFabric"
REPO_DESC="AI量化交易系统 - 支持A股全市场数据 | 针对低配服务器优化"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}  AlphaFabric GitHub 初始化脚本${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""

# 检查 git
if ! command -v git &> /dev/null; then
    echo -e "${RED}错误: 未安装 git${NC}"
    echo "请先安装 git: https://git-scm.com/downloads"
    exit 1
fi

# 检查 GitHub CLI (可选)
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓ 检测到 GitHub CLI${NC}"
    USE_GH=true
else
    echo -e "${YELLOW}⚠ 未检测到 GitHub CLI，将使用 HTTPS 方式${NC}"
    echo "建议安装 GitHub CLI: https://cli.github.com/"
    USE_GH=false
fi

echo ""
echo -e "${YELLOW}配置信息:${NC}"
echo "  GitHub 用户: $GITHUB_USER"
echo "  仓库名称: $REPO_NAME"
echo "  仓库描述: $REPO_DESC"
echo ""

# 初始化 git 仓库
echo -e "${GREEN}步骤 1: 初始化 Git 仓库...${NC}"
if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}✓ Git 仓库初始化完成${NC}"
else
    echo -e "${YELLOW}⚠ Git 仓库已存在${NC}"
fi

# 配置 git 用户信息
echo ""
echo -e "${GREEN}步骤 2: 配置 Git 用户信息...${NC}"
if [ -z "$(git config user.name)" ]; then
    read -p "请输入你的 Git 用户名: " git_name
    git config user.name "$git_name"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "请输入你的 Git 邮箱: " git_email
    git config user.email "$git_email"
fi

echo -e "${GREEN}✓ Git 用户配置完成${NC}"
echo "  用户名: $(git config user.name)"
echo "  邮箱: $(git config user.email)"

# 添加文件
echo ""
echo -e "${GREEN}步骤 3: 添加文件到 Git...${NC}"
git add .
echo -e "${GREEN}✓ 文件已添加${NC}"

# 提交
echo ""
echo -e "${GREEN}步骤 4: 提交代码...${NC}"
git commit -m "Initial commit: AlphaFabric AI量化交易系统

- 支持A股全市场数据
- 5个核心策略
- 30个核心因子
- 2个轻量AI模型
- 完整回测系统
- KIMI CLAW 部署支持"
echo -e "${GREEN}✓ 代码已提交${NC}"

# 创建 GitHub 仓库并推送
echo ""
echo -e "${GREEN}步骤 5: 创建 GitHub 仓库并推送...${NC}"

if [ "$USE_GH" = true ]; then
    # 使用 GitHub CLI
    echo "使用 GitHub CLI 创建仓库..."
    
    # 检查是否已登录
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}请先登录 GitHub CLI:${NC}"
        gh auth login
    fi
    
    # 创建仓库
    gh repo create "$REPO_NAME" \
        --public \
        --description "$REPO_DESC" \
        --source=. \
        --remote=origin \
        --push
    
    echo -e "${GREEN}✓ 仓库创建并推送完成${NC}"
else
    # 使用 HTTPS
    echo "使用 HTTPS 方式推送..."
    
    # 添加远程仓库
    REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
    
    if git remote get-url origin &> /dev/null; then
        git remote set-url origin "$REMOTE_URL"
    else
        git remote add origin "$REMOTE_URL"
    fi
    
    echo -e "${YELLOW}请在 GitHub 上手动创建仓库: https://github.com/new${NC}"
    echo "仓库名称: $REPO_NAME"
    echo ""
    read -p "按回车键继续推送..."
    
    # 推送代码
    git branch -M main
    git push -u origin main
    
    echo -e "${GREEN}✓ 代码已推送到 GitHub${NC}"
fi

# 完成
echo ""
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}  🎉 AlphaFabric 已成功推送到 GitHub!${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo "仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo -e "${YELLOW}后续操作:${NC}"
echo "1. 访问仓库查看代码"
echo "2. 配置 GitHub Secrets (如需 CI/CD)"
echo "3. 部署到 KIMI CLAW"
echo ""
