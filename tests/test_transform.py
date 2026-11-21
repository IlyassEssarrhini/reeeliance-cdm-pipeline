from decimal import Decimal

from src.config import columns
from src.transform_contact import transform_contacts
from src.transform_salesorder import transform_salesorders

def raw_customer(cust_id="CST-001", name="Jane Doe", email="jane@example.com", date="2023-01-15T10:30:00Z", status="active"):
    return {"cust_id": cust_id, "full_name": name, "email_addr": email, "signup_date": date, "user_status": status}

def raw_order(tx_id="ORD-1", customer_id="CST-001", amount="10.5", ts="2023-06-01T09:15:00Z"):
    return {"tx_id": tx_id, "customer_id": customer_id, "amount_usd": amount, "tx_timestamp": ts}

def test_contact_has_exactly_the_cdm_columns_in_order():
    contact = transform_contacts([raw_customer()])[0]
    assert list(contact.keys()) == columns("Contact")

def test_contact_mapping():
    contact = transform_contacts([raw_customer(email="JANE@EXAMPLE.COM", status="ACTIVE")])[0]
    assert contact == {
        "contactid": "CST-001",
        "firstname": "Jane",
        "lastname": "Doe",
        "emailaddress1": "jane@example.com",
        "createdon": "2023-01-15T10:30:00Z",
        "statecode": 0,
    }

def test_duplicate_contact_ids_are_skipped():
    contacts = transform_contacts([raw_customer(), raw_customer()])
    assert len(contacts) == 1


def test_salesorder_has_exactly_the_cdm_columns_in_order():
    orders, _ = transform_salesorders([raw_order()], {"CST-001"})
    assert list(orders[0].keys()) == columns("SalesOrder")


def test_amount_is_decimal_with_two_places():
    orders, _ = transform_salesorders([raw_order(amount="1200")], {"CST-001"})
    assert orders[0]["totalamount"] == Decimal("1200.00")
    assert str(orders[0]["totalamount"]) == "1200.00"


def test_orphan_orders_are_quarantined_not_lost():
    raw = [raw_order("ORD-1", "CST-001"), raw_order("ORD-2", "CST-999")]

    orders, orphans = transform_salesorders(raw, {"CST-001"})

    assert [o["salesorderid"] for o in orders] == ["ORD-1"]
    assert [o["salesorderid"] for o in orphans] == ["ORD-2"]
    # nothing lost: every input record ends up somewhere
    assert len(orders) + len(orphans) == len(raw)