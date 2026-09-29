import re
from typing import List, Dict, Any
from src.utils.logger import get_logger

logger = get_logger("transform.etl_rules")

RULES: Dict[str, callable] = {}