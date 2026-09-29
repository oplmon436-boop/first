import time
import sys
import argparse
from de_project.src.utils.config_loader import load_config
from src.utils.logger import get_logger
from src.extract.reader import read_all
from src.transform.schema_validator import validate_and_split
from src.transform.etl_rules import apply_rules
from src.load.writer import write_output, write_rejections
from src.load.quality import run_checks, QualityCheckFailed






logger = get_logger("pipeline")

def run(config_path: str) -> None:
    start = time.time()
    
  #--- 1. Load config----------------
    logger.info("=" * 60)
    logger.info("ETL PIPELINE STARTING")
    logger.info("=" * 60)
    config = load_config(config_path)
    logger.info(f"Loaded config for job: {config.name} v{config.version}")
    logger.info(f"Description: {config.description}")
    
    #--- 2. Extract----------------
    logger.info("Starting data extraction...")
    raw_records = read_all(config.input)
    logger.info(f"Extracted {len(raw_records)} records from source: {config.input.source_name}")
    
    #---- 3. Validate schema and quality checks (not implemented)----------------
    logger.info("Validating schema and quality checks...")  
    valid_records, rejected_records = validate_and_split(
        raw_records, config.input.input_schema
    )
    logger.info(f"Valid records: {len(valid_records)}, Rejected records: {len(rejected_records)}")
    
    #--- 4.transform----------------
    logger.info("Starting data transformation...")
    transformed = apply_rules(valid_records, config.etl.rules)
    logger.info(f"Transformed {len(transformed)} records")
    
    #--- 5. Load (not implemented)----------------
    logger.info("Loading data to target (not implemented)...")
    output_path = write_output(transformed, config.output)
    logger.info(f"Data loaded to: {output_path}")
    rej_path = write_rejections(rejected_records, config.rejection)
    logger.info(f"Rejected records loaded to: {rej_path}")
    
    #--- 6. quality checks (not implemented)----------------
    logger.info("Performing quality checks (not implemented)...")   
    
    try:
        report = run_checks(
            source_rows = raw_records ,
            valid_rows  = transformed,
            rejected_rows = rejected_records,
            checks_names = config.quality.checks,
            max_rejection_rate = config.rejection.max_rejection_rate
        )
        logger.info(f"Quality checks passed: {report.passed}, failed: {report.failed}")
    except Exception as e:
        logger.error(f"Error during quality checks: {str(e)}")  
        sys.exit(1)
        
    
#--- 7. Finish----------------
    elapsed = round(time.time() - start, 2)
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"  Source rows   : {report.get('rows_source', '?')}")
    logger.info(f"  Valid rows    : {report.get('rows_target', '?')}")
    logger.info(f"  Rejected rows : {report.get('rows_rejected', '?')} "
                f"({report.get('rejection_rate', 0)*100:.2f}%)")
    logger.info(f"  Output        : {output_path}")
    logger.info(f"  Rejected file : {rej_path}")
    logger.info(f"  Duration      : {elapsed}s")
    logger.info("=" * 60)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the E-Commerce ETL pipeline")
    parser.add_argument(
        "--config", default="config/job_config.yaml",
        help="Path to job config YAML"
    )
    args = parser.parse_args()
    run(args.config)