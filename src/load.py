import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def write_csv(records: list[dict], path: Path, columns: list[str]) -> None:
    """Write records to a CSV file with header. None values are written as empty fields."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for record in records:
            writer.writerow({col: "" if record.get(col) is None else record[col] for col in columns})
    logger.info("Wrote %s rows to %s", len(records), path)