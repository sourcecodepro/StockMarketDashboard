import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Configure telemetry logger
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
telemetry_log_path = log_dir / "pipeline_telemetry.log"

logger = logging.getLogger("PipelineTelemetry")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(telemetry_log_path)
file_handler.setFormatter(logging.Formatter('%(message)s'))
if not logger.handlers:
    logger.addHandler(file_handler)


def calculate_dhs(total_fields: int, imputed_fields_count: int) -> Dict[str, Any]:
    """
    Computes Data Health Score (DHS):
    DHS = ((N_required - N_imputed) / N_required) * 100
    """
    if total_fields <= 0:
        dhs = 100.0
    else:
        dhs = round(((total_fields - imputed_fields_count) / total_fields) * 100.0, 1)
        dhs = max(0.0, min(100.0, dhs))

    if dhs >= 90.0:
        status = "High Quality"
        badge_color = "success"
    elif dhs >= 70.0:
        status = "Degraded / Imputed"
        badge_color = "warning"
    else:
        status = "Low Confidence"
        badge_color = "danger"

    return {
        "dhs_score": dhs,
        "status": status,
        "badge_color": badge_color,
        "total_fields": total_fields,
        "imputed_count": imputed_fields_count
    }


def log_telemetry(ticker: str, dhs_info: Dict[str, Any], imputed_fields: List[str], source: str = "yfinance") -> None:
    """Appends structured JSON telemetry records to logs/pipeline_telemetry.log."""
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker,
        "source": source,
        "dhs_score": dhs_info["dhs_score"],
        "status": dhs_info["status"],
        "imputed_fields_count": dhs_info["imputed_count"],
        "imputed_fields": imputed_fields
    }
    logger.info(json.dumps(audit_entry))