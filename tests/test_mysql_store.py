from acfo.mysql_store import map_deleted_entity, map_transaction_line


def test_map_transaction_line():
    row = map_transaction_line(
        {
            "Timestamp": 99,
            "ID": "{AA0273AA-67BC-410B-9321-F27C40AF22A9}",
            "Division": 1234,
            "EntryID": "BB0273AA-67BC-410B-9321-F27C40AF22A9",
            "EntryNumber": 20240012,
            "LineNumber": 1,
            "Date": "/Date(1609459200000)/",
            "AmountDC": 12.5,
            "GLAccountCode": "1300",
            "Type": 20,
            "Status": 50,
        }
    )
    assert row["id"] == "aa0273aa-67bc-410b-9321-f27c40af22a9"
    assert row["entry_id"] == "bb0273aa-67bc-410b-9321-f27c40af22a9"
    assert row["timestamp"] == 99
    assert row["amount_dc"] == 12.5
    assert row["gl_account_code"] == "1300"
    assert row["deleted_at"] is None
    assert row["date"].isoformat() == "2021-01-01"


def test_map_deleted_entity_uses_entity_key():
    row = map_deleted_entity(
        {
            "ID": "cc0273aa-67bc-410b-9321-f27c40af22a9",
            "EntityKey": "aa0273aa-67bc-410b-9321-f27c40af22a9",
            "EntityType": 1,
            "Timestamp": 150,
            "Division": 1234,
        }
    )
    assert row["entity_key"] == "aa0273aa-67bc-410b-9321-f27c40af22a9"
    assert row["entity_type"] == 1
    assert row["id"] != row["entity_key"]
