import os
import rule
import yaml
import account

# Menu
def menu(config):
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
            account.transaction(config)
        elif choice == 'i':
            rule.rule(config)
        elif choice == 'p':
            account.statement(config)
        else:
            print(f"Thank you for banking with {config["bank_name"]}. \nHave a nice day!")
            break


if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    account = account.Account()

    print(f"Welcome to {config["settings"]["bank_name"]}! What would you like to do?")
    menu(config["settings"])