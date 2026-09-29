"""extract/reader.py – Reads all CSV files from the configured input path."""

import os
import csv
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.config_loader import InputConfig

logger = get_logger("extract.reader")

def read_all(config: InputConfig) -> List[Dict[str, Any]]:
    """
    Scan input_path for files matching input_suffix.
    Returns a flat list of raw row dicts.
    """
    records = []
    path = config.input_path
    suffix = config.input_suffix

    files = [f for f in os.listdir(path) if f.endswith(suffix)]
    if not files:
        raise FileNotFoundError(f"No {suffix} files found in {path}")

    for filename in sorted(files):
        filepath = os.path.join(path, filename)
        batch = _read_csv(filepath)
        logger.info(f"Loaded {len(batch):>5} rows  <-  {filename}")
        records.extend(batch)

    logger.info(f"Extract complete – total rows: {len(records)}")
    return records

def _read_csv(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]