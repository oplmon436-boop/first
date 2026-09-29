from typing import List, Dict, Any, Tuple
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger("transform.schema_validator")
TYPE_CASTERS = {
    "str":   str,
    "int":   int,
    "float": float,
}

def validate_and_split( 
                       records: List[Dict[str, Any]],
                        schema: Dict[str, str]
                        ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    
    valid , rejected = [], []
    
    for row in records:
        reason = _check_row(row, schema)
        if reason:
            row["_rejection_reason"] = reason
            rejected.append(row)
        else:
            valid.append(_cast_row(row, schema))
            
    pct = len(rejected) / max(len(records), 1) * 100
    logger.info(
        f"Schema validation – valid: {len(valid)}, rejected: {len(rejected)} ({pct:.1f}%)"
    )
    return valid, rejected


def _check_row(row: Dict[str, Any], schema: Dict[str, str]) -> str:
    
        # 1. Required fields present & non-empty
    for col in ("order_id", "customer_id", "product_id"):
        if not row.get(col, "").strip():
            return f"missing required field: {col}"
        
        # 2. Numeric fields castable
    for col, typ in schema.items():
        val = row.get(col, "")
        if typ in ("int", "float") and val == "":
            return f"empty numeric field: {col}"
        if typ in ("int", "float"):
            try:
                TYPE_CASTERS[typ](val)
            except (ValueError, TypeError):
                return f"cannot cast {col}='{val}' to {typ}"
        
    
        # 3. Quantity > 0
    try:
        if int(row.get("quantity", 0)) <= 0:
            return "quantity must be > 0"
    except ValueError:
        return "quantity is not numeric"

    # 4. Price > 0
    try:
        if float(row.get("unit_price", 0)) <= 0:
            return "unit_price must be > 0"
    except ValueError:
        return "unit_price is not numeric"
    
    try:
        order_dt = datetime.strptime(row.get("order_date", ""), "%Y-%m-%d")
        if order_dt > datetime.today():
            return f"order_date {row['order_date']} is in the future"
    except ValueError:
        return f"invalid order_date format: {row.get('order_date')}"

    return ""


def _cast_row(row: Dict, schema: Dict[str, str]) -> Dict:
    """Return a new dict with values cast to their declared Python types."""
    out = {}
    for col, typ in schema.items():
        val = row.get(col, "")
        out[col] = TYPE_CASTERS.get(typ, str)(val) if val != "" else None
    return out