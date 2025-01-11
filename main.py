import os
import yaml

from account import Account
from compute_transaction import ComputeTransaction
from rule import Rule

# Menu
def main(config, account, rule, compute_transaction):

    while True:
        print(f"[T] {config['menu_transaction']}")
        print(f"[I] {config['menu_rules']}")
        print(f"[P] {config['menu_statement']}")
        print(f"[Q] {config['menu_quit']}")

        choice = input("> ")
        choice = choice.lower()

        # Menu validation
        if not choice.isalpha():
            print("Please enter only alphabetical character")
            continue
        elif choice.isalpha() and choice not in ['t', 'i', 'p', 'q']:
            print("Please enter a valid option")
            continue

        if choice == 't':
            account.transactions_input()
            print(f"{config["menu_continue"]}")
        elif choice == 'i':
            rule.interest_input()
            print(f"{config["menu_continue"]}")
        elif choice == 'p':
            compute_transaction.print_input(account, rule)
            print(f"{config["menu_continue"]}")
        else:
            print(f"Thank you for banking with {config["bank_name"]}. \nHave a nice day!")
            break


if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = config["settings"]
    account = Account(config)
    rule = Rule(config)
    compute_transaction = ComputeTransaction(config)

    print(f"Welcome to {config["bank_name"]}! What would you like to do?")
    main(config, account, rule, compute_transaction)