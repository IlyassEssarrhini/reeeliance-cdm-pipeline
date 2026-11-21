from src.extract import read_csv_records

def test_read_csv_records_repairs_record_split_over_two_lines(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        "cust_id,full_name,email_addr,signup_date,user_status\n"
        "CST-001,Jane Doe,jane.doe@example.com,2023-01-15T10:30:00Z,active\n"
        "CST-005, Charlie Brown\n"
        ",charlie@peanuts.com,2023-05-01T12:00:00Z,inactive\n",
        encoding="utf-8",
    )

    records = read_csv_records(csv_file)

    assert len(records) == 2
    assert records[1] == {
        "cust_id": "CST-005",
        "full_name": " Charlie Brown",
        "email_addr": "charlie@peanuts.com",
        "signup_date": "2023-05-01T12:00:00Z",
        "user_status": "inactive",
    }

def test_read_csv_records_drops_incomplete_last_records(tmp_path):
    csv_file = tmp_path / "broken.csv"
    csv_file.write_text("a,b,c\n1,2,3\n4,5\n", encoding="utf-8")

    records = read_csv_records(csv_file)

    assert records == [{"a": "1", "b": "2", "c": "3"}]