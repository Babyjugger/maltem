import pytest
from unittest.mock import patch, MagicMock
import sys
import os
# import main  # Import your `main` module.

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure correct imports for main.py

from main import main



@pytest.fixture
def config_mock():
    """Mock configuration settings used in the application."""
    return {
        "menu_transaction": "Transactions",
        "menu_rules": "Rules",
        "menu_statement": "Print Statement",
        "menu_quit": "Quit",
        "menu_continue": "Press Enter to continue...",
        "bank_name": "Mock Bank"
    }


@pytest.fixture
def mock_classes():
    """Mock dependencies: Account, Rule, and ComputeTransaction."""
    account = MagicMock()
    rule = MagicMock()
    compute_transaction = MagicMock()

    return account, rule, compute_transaction


def test_main_menu_transaction(config_mock, mock_classes):
    """Test the transaction menu option 'T'."""
    account, rule, compute_transaction = mock_classes

    with patch("builtins.input", side_effect=["t", "q"]), patch("builtins.print") as mock_print:
        main(config_mock, account, rule, compute_transaction)

        assert account.transactions_input.called, "Transactions input should be called."
        assert "Press Enter to continue..." in [call.args[0] for call in mock_print.call_args_list]


def test_main_menu_rules(config_mock, mock_classes):
    """Test the rules menu option 'I'."""
    account, rule, compute_transaction = mock_classes

    with patch("builtins.input", side_effect=["i", "q"]), patch("builtins.print") as mock_print:
        main(config_mock, account, rule, compute_transaction)

        assert rule.interest_input.called, "Interest input should be called."
        assert "Press Enter to continue..." in [call.args[0] for call in mock_print.call_args_list]


def test_main_menu_print_statement(config_mock, mock_classes):
    """Test the print statement menu option 'P'."""
    account, rule, compute_transaction = mock_classes

    with patch("builtins.input", side_effect=["p", "q"]), patch("builtins.print") as mock_print:
        main(config_mock, account, rule, compute_transaction)

        assert compute_transaction.print_input.called, "Print input should be called with account and rule."
        assert "Press Enter to continue..." in [call.args[0] for call in mock_print.call_args_list]


def test_main_menu_quit(config_mock, mock_classes):
    """Test the quit menu option 'Q'."""
    account, rule, compute_transaction = mock_classes

    with patch("builtins.input", side_effect=["q"]), patch("builtins.print") as mock_print:
        main(config_mock, account, rule, compute_transaction)

        quit_message = f"Thank you for banking with {config_mock['bank_name']}. \nHave a nice day!"
        assert quit_message in [call.args[0] for call in mock_print.call_args_list], "Quit message was not printed."


def test_main_invalid_input(config_mock, mock_classes):
    """Test handling invalid input."""
    account, rule, compute_transaction = mock_classes

    with patch("builtins.input", side_effect=["123", "@", "invalid", "q"]), patch("builtins.print") as mock_print:
        main(config_mock, account, rule, compute_transaction)

        error_messages = [
            "Please enter only alphabetical character",
            "Please enter a valid option"
        ]
        printed_messages = [call.args[0] for call in mock_print.call_args_list]

        for message in error_messages:
            assert message in printed_messages, f"Error message '{message}' was not printed as expected."