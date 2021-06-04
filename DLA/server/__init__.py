from typing import Any, Dict, Final

config_dict: Dict[str, Any]
SUCCESS: Final[bytes] = b'\00'
FAIL: Final[bytes] = b'\01'
