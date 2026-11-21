"""Integration test: run the whole pipeline on the real raw data into a temp folder."""
import csv
import json

import pytest

from src import main

@pytest.fixture
def output_dir(tmp_path, monkeypatch):
    out = tmp_path / "cdm_lakehouse"
    monkeypatch.setattr(main, "OUTPUT_DIR", out)
    main.run()
    return out

def read_rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_output_files_exist(output_dir):
    assert (output_dir / "Contact" / "Contact.csv").exists()
    assert (output_dir / "SalesOrder" / "SalesOrder.csv").exists()
    assert (output_dir / "model.json").exists()

def test_row_counts_match_source(output_dir):
    contacts = read_rows(output_dir / "Contact" / "Contact.csv")
    orders = read_rows(output_dir / "SalesOrder" / "SalesOrder.csv")
    orphans = read_rows(output_dir / "_rejected" / "SalesOrder_orphans.csv")

    assert len(contacts) == 5  # all 5 customers, incl. repaired CST-005
    assert len(orders) == 4  # ORD-1005 is an orphan
    assert len(orders) + len(orphans) == 5  # no order lost


def test_referential_integrity(output_dir):
    contact_ids = {r["contactid"] for r in read_rows(output_dir / "Contact" / "Contact.csv")}
    orders = read_rows(output_dir / "SalesOrder" / "SalesOrder.csv")
    assert all(o["customerid"] in contact_ids for o in orders)


def test_manifest_matches_output(output_dir):
    manifest = json.loads((output_dir / "model.json").read_text(encoding="utf-8"))

    assert {e["name"] for e in manifest["entities"]} == {"Contact", "SalesOrder"}
    for entity in manifest["entities"]:
        csv_path = output_dir / entity["partitions"][0]["location"]
        assert csv_path.exists()
        with open(csv_path, encoding="utf-8") as f:
            header = next(csv.reader(f))
        assert header == [a["name"] for a in entity["attributes"]]

    rel = manifest["relationships"][0]
    assert rel["fromAttribute"] == {"entityName": "SalesOrder", "attributeName": "customerid"}
    assert rel["toAttribute"] == {"entityName": "Contact", "attributeName": "contactid"}