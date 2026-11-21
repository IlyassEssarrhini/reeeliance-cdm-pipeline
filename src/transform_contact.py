import logging

from src.config import columns
from src.validators import map_statecode, normalize_email, parse_datetime, split_name

logger = logging.getLogger(__name__)

def transform_contacts(raw_records: list[dict]) -> list[dict]:
    """Map raw customer records to the CDM contact entity."""
    contacts = []
    seen_ids = set()

    for raw in raw_records:
        contact_id = (raw.get("cust_id") or "").strip()

        # Primary key checks: must exist and be unique
        if not contact_id:
            logger.error("Customer record without cust_id skipped: %r", raw)
            continue
        if contact_id in seen_ids:
            logger.error("Duplicate contactid %s skipped", contact_id)
            continue
        seen_ids.add(contact_id)

        firstname, lastname = split_name(raw.get("full_name"))

        contact = {
            "contactid": contact_id,
            "firstname": firstname,
            "lastname": lastname,
            "emailaddress1": normalize_email(raw.get("email_addr"), contact_id),
            "createdon": parse_datetime(raw.get("signup_date"), contact_id),
            "statecode": map_statecode(raw.get("user_status"), contact_id),
        }
        # Keep the column order defined in the CDM schema
        contacts.append({col: contact[col] for col in columns("Contact")})

    logger.info("Transformed %s of %s customer records into Contact", len(contacts), len(raw_records))
    return contacts