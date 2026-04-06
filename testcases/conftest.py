# testcases/conftest.py
"""pytest 公共配置：将项目根目录加入 Python 路径。"""

import sys
from pathlib import Path

# testcases/ 的上一级即项目根目录，保证 `from config.settings` 等导入可用
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
