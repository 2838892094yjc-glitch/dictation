#!/bin/bash
# 自动听写软件测试脚本
# 用法: ./run_tests.sh [选项]
#   -a, --all       运行所有测试（包括慢速测试）
#   -f, --fast      只运行快速测试（默认）
#   -c, --coverage  生成覆盖率报告
#   -v, --verbose   详细输出
#   -h, --help      显示帮助

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认选项
RUN_ALL=false
COVERAGE=false
VERBOSE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        -f|--fast)
            RUN_ALL=false
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "用法: ./run_tests.sh [选项]"
            echo "  -a, --all       运行所有测试（包括慢速测试）"
            echo "  -f, --fast      只运行快速测试（默认）"
            echo "  -c, --coverage  生成覆盖率报告"
            echo "  -v, --verbose   详细输出"
            echo "  -h, --help      显示帮助"
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            exit 1
            ;;
    esac
done

# 切换到项目目录
cd "$(dirname "$0")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    自动听写软件 - 测试套件${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查pytest是否安装
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}错误: pytest未安装${NC}"
    echo "请运行: pip install pytest pytest-cov pytest-timeout"
    exit 1
fi

# 构建pytest命令
PYTEST_CMD="python -m pytest tests/"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$RUN_ALL" = false ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
    echo -e "${YELLOW}模式: 快速测试（跳过慢速测试）${NC}"
else
    echo -e "${YELLOW}模式: 完整测试（包括慢速测试）${NC}"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov=data --cov-report=html --cov-report=term-missing"
    echo -e "${YELLOW}覆盖率: 启用${NC}"
fi

echo ""
echo -e "${GREEN}运行命令: $PYTEST_CMD${NC}"
echo ""

# 运行测试
$PYTEST_CMD

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    所有测试通过！${NC}"
    echo -e "${GREEN}========================================${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}覆盖率报告已生成: htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}    测试失败！${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
