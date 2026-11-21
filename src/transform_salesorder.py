import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from src.config import columns
from src.validators import parse_datetime


logger = logging.getLogger(__name__)

def parse_amount(value: str, record_id: str = "") -> Decimal | None:
    """Parse an amount into a Decimal with 2 decimal places. Invalid values return None."""
    try:
        return Decimal((value or "").strip()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        logger.warning("Invalid amount for %s: %r -> set to null", record_id, value)
        return None


def transform_salesorders(raw_records: list[dict], valid_contact_ids: set[str]) -> tuple[list[dict] ,list[dict]]:
    """Map raw order records to the CDM SalesOrder entity.

    Returns (orders, orphans). Orders whose customerid does not exist in Contact are orphans:
    they are logged and returned separately instead of being written to SalesOrder.csv, so referential integriry is kept and nothing is lost silently."""
    orders, orphans = [], []
    seen_ids = set()

    for raw in raw_records:
        order_id = (raw.get("tx_id") or "").strip()

        if not order_id:
            logger.error("Order record without tx_id skipped: %r", raw)
            continue
        if order_id in seen_ids:
            logger.error("Duplicate salesorderid %s skipped", order_id)
            continue
        seen_ids.add(order_id)

        order = {
            "salesorderid": order_id,
            "customerid": (raw.get("customer_id") or "").strip(),
            "totalamount": parse_amount(raw.get("amount_usd"), order_id),
            "createdon": parse_datetime(raw.get("tx_timestamp"), order_id),
        }
        order =  {col: order[col] for col in columns("SalesOrder")}

        # foreign key check: customerid must reference an existing Contact
        if order["customerid"] not in valid_contact_ids:
            logger.warning("orphan order %s: customerid %s not found in Contact -> quarantined", order_id, order["customerid"])
            orphans.append(order)
            continue

        orders.append(order)

    logger.info("Transformed %s of %s order records into SalesOrder (%s orphans)",len(orders), len(raw_records), len(orphans))
    return orders, orphans