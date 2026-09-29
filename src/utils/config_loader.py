"""utils/config_loader.py – Parses job_config.yaml into a typed dataclass."""

import yaml
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class InputConfig:
    source_name: str
    input_type: str
    input_path: str
    input_suffix: str
    has_header: bool
    input_schema: dict
    
    
@dataclass
class RejectionConfig:
    rejection_path: str
    rejection_type: str
    max_rejection_rate: float
    
    
@dataclass
class OutputConfig:
    target_table: str
    output_type: str
    output_path: str
    save_mode: str
    partition_cols: List[str] = field(default_factory=list)
    
    

@dataclass
class ETLConfig:
    rules: List[dict] = field(default_factory=list)
    
@dataclass
class QualityConfig:
    checks: List[str] = field(default_factory=list)
    
@dataclass
class JobConfig:
    name: str
    version: str
    description: str
    input: InputConfig
    rejection: RejectionConfig
    output: OutputConfig
    etl: ETLConfig
    quality: QualityConfig
    
def load_config(path: str) -> JobConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)

    return JobConfig(
        name        = raw["job"]["name"],
        version     = raw["job"]["version"],
        description = raw["job"]["description"],
        input       = InputConfig(**raw["input"]),
        rejection   = RejectionConfig(**raw["rejection"]),
        output      = OutputConfig(**raw["output"]),
        etl         = ETLConfig(rules=raw["etl"]["rules"]),
        quality     = QualityConfig(checks=raw["quality"]["checks"]),
    )
        
