import pytest
import pandas as pd
import sys
import os
from unittest.mock import patch
# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure correct imports for main.py

from account import Account

# Mock configuration
@pytest.fixture
def mock_config():
    return {
        "date_col": "date",
        "tansaction_col": "transaction_code",
        "type_col": "type",
        "amount_col": "amount",
        "account_title": "Account Balance",
        "transaction_input": "Enter transaction details (YYYYmmdd AccountID D/W Amount)",
        "empty_input": "Press enter without input to exit",
    }


# Test cases
@pytest.fixture
def test_account(mock_config):
    # Create an Account instance with mocked config
    account = Account(mock_config, test_enabled=True)

    # Add sample data
    account.df = pd.DataFrame(
        {
            "account_id": ["AC001", "AC001", "AC002"],
            "date": [20230101, 20230102, 20230101],
            "transaction_code": ["20230101-01", "20230102-01", "20230101-01"],
            "type": ["D", "W", "D"],
            "amount": [100.0, 50.0, 200.0],
            "balance": [100.0, 50.0, 200.0],  # Pre-calculated values
        }
    )
    return account


# Test compute_balance
def test_compute_balance(test_account):
    """Test that balances are computed correctly."""
    test_account.compute_balance("AC001")
    assert test_account.df.loc[0, "balance"] == 100.0
    assert test_account.df.loc[1, "balance"] == 50.0  # 100 - 50


# Test clean_transaction
def test_clean_transaction(test_account):
    """Test that a transaction is added successfully and balance is updated."""
    test_account.clean_transaction(20230103, "AC001", "D", 200.0)  # Deposit 200
    latest_transaction = test_account.df.iloc[-1]

    assert latest_transaction["account_id"] == "AC001"
    assert latest_transaction["date"] == 20230103
    assert latest_transaction["type"] == "D"
    assert latest_transaction["amount"] == 200.0
    assert latest_transaction["balance"] == 250.0  # Previous balance (50) + 200


# Test validate_transactions_input - valid case
@patch("account.validate_date_format", return_value=True)  # Patch where the function is used
@patch("account.validate_amount", return_value=True)
def test_validate_transactions_input_valid(mock_validate_date, mock_validate_amount, test_account):
    """Test valid input for input validation."""
    response = "20230105 AC001 D 300"
    assert test_account.validate_transactions_input(response) is True


# Test validate_transactions_input - invalid date
@patch("account.validate_date_format", return_value=False)  # Invalid date
@patch("account.validate_amount", return_value=True)
def test_validate_transactions_input_invalid_date(mock_validate_date, mock_validate_amount, test_account):
    """Test invalid date format for validation."""
    response = "INVALID-DATE AC001 D 300"
    assert test_account.validate_transactions_input(response) is False


# Test validate_transactions_input - withdrawal exceeds balance
@patch("account.validate_date_format", return_value=True)
@patch("account.validate_amount", return_value=True)
def test_validate_transactions_input_exceeds_balance(mock_validate_date, mock_validate_amount, test_account):
    """Test withdrawal when balance is insufficient."""
    response = "20230107 AC001 W 100"  # Current balance for 001 is 50
    assert test_account.validate_transactions_input(response) is False


# Test clean_transaction with a new account
def test_clean_transaction_new_account(test_account):
    """Test adding a new transaction for a new account."""
    test_account.clean_transaction(20230101, "AC003", "D", 500.0)  # Deposit to new account

    new_account_transaction = test_account.df[test_account.df["account_id"] == "AC003"].iloc[0]
    assert new_account_transaction["account_id"] == "AC003"
    assert new_account_transaction["amount"] == 500.0
    assert new_account_transaction["balance"] == 500.0


# Test compute_balance for empty account
def test_compute_balance_empty(test_account):
    """Test edge case where no transactions exist for the account."""
    test_account.df = pd.DataFrame(columns=["account_id", "date", "transaction_code", "type", "amount", "balance"])
    test_account.compute_balance("999")  # Non-existent account
    assert test_account.df.empty


if __name__ == "__main__":
    pytest.main()
