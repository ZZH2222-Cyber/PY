#!/usr/bin/env python
# runtest.py
"""测试执行入口：支持多种运行模式、Allure 报告生成、命令行参数解析。"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DATA_DIR, LOG_DIR, REPORT_DIR

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """配置控制台日志输出。

    参数：
        无

    返回：
        无
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_pytest(
    test_path: Optional[str] = None,
    markers: Optional[str] = None,
    allure: bool = False,
    extra_args: Optional[List[str]] = None,
) -> int:
    """执行 pytest 测试。

    参数：
        test_path: 测试文件或目录路径，默认运行 testcases/ 下所有用例。
        markers: pytest 标记过滤，如 "login" 或 "security"。
        allure: 是否生成 Allure 报告。
        extra_args: 额外的 pytest 命令行参数。

    返回：
        pytest 退出码（0 表示成功，非 0 表示失败）。

    异常：
        无。
    """
    cmd: List[str] = ["pytest"]

    # 测试路径
    if test_path:
        # 如果不是绝对路径，则在 testcases 目录下查找
        if not os.path.isabs(test_path):
            # 支持简写：test_login → testcases/test_login.py
            if not test_path.endswith(".py"):
                test_path = f"testcases/{test_path}.py"
            else:
                test_path = f"testcases/{test_path}"
        cmd.append(test_path)
    else:
        cmd.append(str(PROJECT_ROOT / "testcases"))

    # 默认参数
    cmd.extend(["-v", "--tb=short", "-W", "ignore::DeprecationWarning"])

    # 标记过滤
    if markers:
        cmd.extend(["-m", markers])

    # Allure 报告
    if allure:
        from pathlib import Path as PathLib
        allure_dir = PathLib(REPORT_DIR) / "allure_results"
        allure_dir.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--alluredir", str(allure_dir)])

    # 额外参数
    if extra_args:
        cmd.extend(extra_args)

    logger.info("执行命令：%s", " ".join(cmd))
    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


def generate_allure_report() -> int:
    """生成 Allure HTML 报告。

    参数：
        无

    返回：
        命令退出码。

    异常：
        无。
    """
    from pathlib import Path as PathLib
    allure_results = PathLib(REPORT_DIR) / "allure_results"
    allure_report = PathLib(REPORT_DIR) / "allure_report"

    if not allure_results.exists():
        logger.error("Allure 结果目录不存在：%s，请先运行测试", allure_results)
        return 1

    cmd = ["allure", "generate", str(allure_results), "-o", str(allure_report), "--clean"]
    logger.info("生成 Allure 报告：%s", " ".join(cmd))
    return subprocess.run(cmd).returncode


def open_allure_report() -> int:
    """打开 Allure 报告（启动本地服务器）。

    参数：
        无

    返回：
        命令退出码。

    异常：
        无。
    """
    from pathlib import Path as PathLib
    allure_results = PathLib(REPORT_DIR) / "allure_results"

    if not allure_results.exists():
        logger.error("Allure 结果目录不存在：%s，请先运行测试", allure_results)
        return 1

    cmd = ["allure", "serve", str(allure_results)]
    logger.info("启动 Allure 报告服务：%s", " ".join(cmd))
    return subprocess.run(cmd).returncode


def create_directories() -> None:
    """创建必要的目录结构。

    参数：
        无

    返回：
        无
    """
    from pathlib import Path
    for dir_path in [DATA_DIR, REPORT_DIR, LOG_DIR]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    logger.info("目录结构检查完成")


def main() -> int:
    """主函数：解析命令行参数并执行测试。

    参数：
        无

    返回：
        退出码（0 表示成功）。

    异常：
        无。
    """
    setup_logging()

    parser = argparse.ArgumentParser(
        description="接口自动化测试框架 - 执行入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python runtest.py                      # 运行所有测试
  python runtest.py -t test_login        # 运行指定测试文件
  python runtest.py -m login             # 运行带 login 标记的测试
  python runtest.py --allure             # 运行测试并生成 Allure 报告
  python runtest.py --allure --open      # 生成并打开 Allure 报告
  python runtest.py --report             # 仅生成 Allure HTML 报告
        """,
    )

    parser.add_argument(
        "-t", "--test",
        dest="test_path",
        help="指定测试文件或目录路径",
    )
    parser.add_argument(
        "-m", "--marker",
        dest="markers",
        help="pytest 标记过滤（如 login, security）",
    )
    parser.add_argument(
        "--allure",
        action="store_true",
        help="生成 Allure 报告数据",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="打开 Allure 报告（需配合 --allure 使用）",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="仅生成 Allure HTML 报告（不运行测试）",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化项目目录结构",
    )
    parser.add_argument(
        "extra",
        nargs="*",
        help="额外的 pytest 参数（如 -k 'test_login'）",
    )

    args = parser.parse_args()

    # 初始化目录
    if args.init:
        create_directories()
        return 0

    # 仅生成报告
    if args.report:
        return generate_allure_report()

    # 创建目录
    create_directories()

    # 运行测试
    exit_code = run_pytest(
        test_path=args.test_path,
        markers=args.markers,
        allure=args.allure,
        extra_args=args.extra if args.extra else None,
    )

    # 打开 Allure 报告
    if args.allure and args.open:
        open_allure_report()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())