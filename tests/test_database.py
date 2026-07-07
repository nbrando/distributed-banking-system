import uuid
import pytest
from bdb_server.database import Database


db = Database("tests/test_data/test.db")


@pytest.fixture()
def clean_db():
    db.conn.execute("DELETE FROM accounts")
    db.conn.execute("DELETE FROM transfers")
    db.conn.commit()
    db.seed()

    return db


# Check initial seed balances
def test_seed_balances(clean_db):
    assert db.balance("1") == 500000
    assert db.balance("2") == 1000

# Check balance of a made up account
def test_balance_fake(clean_db):
    assert db.balance("999") is None

# Test a succesfull transfer
def test_tansfer_succeeds(clean_db):
    trans_id = str(uuid.uuid4())
    result = db.transfer(trans_id, "1", "2", 100000, 0)
    assert result["status"] == "COMPLETED"
    assert db.balance("1") == 400000
    assert db.balance("2") == 101000

# Test fees deducting properly
def test_fees(clean_db):
    # base amount 300000 + fee 2000 = 302000 taken from sender
    # but only 300000 goes to the recipient
    trans_id = str(uuid.uuid4())
    db.transfer(trans_id, "1", "2", 300000, 2000)
    assert db.balance("1") == 198000
    assert db.balance("2") == 301000

# Test poor people
def test_no_money(clean_db):
    trans_id = str(uuid.uuid4())
    result = db.transfer(trans_id, "1", "2", 99999900, 0)
    assert result["status"] == "FAILED: Insufficient funds"
    assert db.balance("1") == 500000     

# Test transfer to made up person
def test_invalid_recipient(clean_db):
    trans_id = str(uuid.uuid4())
    result = db.transfer(trans_id, "1", "999", 10000, 0)
    assert result["status"] == "FAILED: Invalid recipient"
    assert db.balance("1") == 500000      # Unchanged
    assert db.balance("999") is None   # Still doesn't exist

# Test if recording correctly
def test_transfer_logs(clean_db):
    trans_id = str(uuid.uuid4())
    db.transfer(trans_id, "1", "999", 10000, 0)
    record = db.status(trans_id)
    assert record is not None              
    assert record["status"] == "FAILED: Invalid recipient"

# Test idempotency
def test_duplicates(clean_db):
    trans_id = str(uuid.uuid4())
    db.transfer(trans_id, "1", "2", 100000, 0)
    db.transfer(trans_id, "1", "2", 100000, 0)  

    assert db.balance("1") == 400000
    assert db.balance("2") == 101000

# Test fake transfer status
def test_get_transfer(clean_db):
    assert db.status("nonexistent") is None