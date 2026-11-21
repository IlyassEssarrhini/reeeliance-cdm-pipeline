"""Pipeline entry point: extract -> transform -> load -> manifest.

Run from the project root with: python -m src.main
"""

import logging

from src.config import LOG_DIR, OUTPUT_DIR, RAW_CUSTOMERS, RAW_ORDERS, columns
from src.extract import read_csv_records
from src.load import write_csv
from src.manifest import build_manifest, write_manifest
from src.transform_contact import transform_contacts
from src.transform_salesorder import transform_salesorders

PARTITIONS = {
    "Contact": "Contact/Contact.csv",
    "SalesOrder": "SalesOrder/SalesOrder.csv",
}

def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "pipeline.log", mode="w", encoding="utf-8"),
        ],
    )


def run() -> None:
    logger = logging.getLogger("pipeline")
    logger.info("Pipeline started")

    # Extraction
    raw_customers = read_csv_records(RAW_CUSTOMERS)
    raw_orders = read_csv_records(RAW_ORDERS)

    # Transforming (Contract fist: SalesOrder needs the valid contract IDs for the FK check)
    contacts = transform_contacts(raw_customers)
    contact_ids = {c["contactid"] for c in contacts}
    orders, orphans = transform_salesorders(raw_orders, contact_ids)

    # Loading
    write_csv(contacts, OUTPUT_DIR / PARTITIONS["Contact"], columns("Contact"))
    write_csv(orders, OUTPUT_DIR / PARTITIONS["SalesOrder"], columns("SalesOrder"))
    if orphans:
        write_csv(orphans, OUTPUT_DIR / "_rejected" /"SalesOrder_orphans.csv", columns("SalesOrder"))

    # Manifesting
    write_manifest(build_manifest(PARTITIONS), OUTPUT_DIR / "model.json")

    logger.info(
        "Pipeline finished: %s contacts, %s orders, %s orphans orders quarantined", len(contacts), len(orders), len(orphans),
    )

if __name__ == "__main__":
    setup_logging()
    run()