"""Central configuration: paths and the CDM schema (single source of truth)."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT /"data" / "raw"
OUTPUT_DIR = PROJECT_ROOT /"cdm_lakehouse"
LOG_DIR = PROJECT_ROOT / "logs"

RAW_CUSTOMERS = RAW_DIR / "raw_customers.csv"
RAW_ORDERS = RAW_DIR / "raw_orders.csv"

# CDM schema: used fro CSV column order AND for model.json
CDM_ENTITIES = {
    "Contact": {
        "descriptiopn": "Standard CDM Contract entity for individual customers",
        "attributes": [
            ("contactid", "string", "Unique primary key for the contact"),
            ("firstname", "string", "First name of the contact"),
            ("lastname", "string", "Last name of the contact"),
            ("emailaddress1", "string", "Primary email address"),
            ("createdon", "datetime", "ISO 8601 creation timestamp"),
            ("statecode", "int64", "Status code: 0 for active, 1 for inactive"),
        ],
    },
    "SalesOrder": {
        "description": "Standard CDM SalesOrder entity for transactions",
        "attributes": [
            ("salesorderid", "string", "Unique order identifier"),
            ("customerid", "string", "Foreign Key reference to Contact"),
            ("totalamount", "decimal", "Total order amount in USD"),
            ("createdon", "dateTime", "ISO 8691 transaction timestamp"),
        ],
    },
}

def columns(entity: str) -> list[str]:
    """Return the order column names of a CDM entity."""
    return [name for name, _, _ in CDM_ENTITIES[entity]["attributes"]]