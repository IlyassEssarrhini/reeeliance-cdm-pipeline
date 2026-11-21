import json
import logging
from pathlib import Path

from src.config import CDM_ENTITIES

logger = logging.getLogger(__name__)


def build_manifest(partitions: dict[str, str]) -> dict:
    """Build a CDM model.json manifest from the central schema in config.py.

    Partitions maps entity name -> relative file location, e.g. {"Contact": "Contact/Contact.csv"}.
    """
    entities = []
    for name, spec in CDM_ENTITIES.items():
        entities.append({
            "$type": "LocalEntity",
            "name": name,
            "description": spec["description"],
            "attributes": [
                {"name": attr, "dataType": dtype, "description": desc}
                for attr, dtype, desc in spec["attributes"]
            ],
            "partitions": [{
                "name": f"{name}Partitions",
                "location": partitions[name],
                "fileFormatSettings": {
                    "$type": "CsvFormatSettings",
                    "columnHeaders": True,
                    "delimiter": ",",
                },
            }],
        })

    return {
        "name": "EnterpriseDataLake",
        "description": "CDM Manifest for Ingested Customer and Sales Data",
        "version": "1.0",
        "entities": entities,
        "relationships": [{
            "$type": "SingleKeyRelationship",
            "name": "Contact_SalesOrder_Relationship",
            "fromAttribute": {"entityName": "SalesOrder", "attributeName": "customerid"},
            "toAttribute": {"entityName": "Contact", "attributeName": "contactid"},
        }],
    }


def write_manifest(manifest: dict, path: Path) -> None:
    """Write the manifest as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Wrote manifest to %s", path)