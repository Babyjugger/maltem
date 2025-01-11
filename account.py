import os
import pandas as pd
from helper import validate_date_format, validate_amount
from datetime import datetime

class Account:
    def __init__(self, config, test_enabled=False):

        self.df = None
        self.config = config

        if not test_enabled:
            filename = "/data.txt"
            pd.options.display.float_format = "{:,.2f}".format
            self.df = pd.read_csv(os.path.dirname(os.path.realpath(__file__)) + filename, delimiter=',', encoding="utf-8", skipinitialspace=True)

        if self.df is None:
            self.df = pd.DataFrame(columns=['account_id', 'date', 'transaction_code', 'type', 'amount', 'balance'])

    def compute_balance(self, account):
        account_balances = self.df.sort_values(by=["transaction_code"])
        new_balance = 0.0
        for index, row in account_balances.iterrows():
            if row["account_id"] == account:
                if row["type"] == "D":
                    new_balance += row["amount"]
                elif row["type"] == "W":
                    new_balance -= row["amount"]

                account_balances.at[index, "balance"] = new_balance

        self.df = account_balances


    def clean_transaction(self, date, account, type, amount):
        # Filter transactions for the same account_id and date
        self.df["date"] = pd.to_numeric(self.df["date"], downcast='integer', errors='coerce')
        filtered_df = self.df[(self.df["account_id"] == account) & (self.df["date"] == int(date))]
        # Determine the latest running number
        if not filtered_df.empty:
            latest_transaction_code = filtered_df["transaction_code"].max()
            latest_running_number = int(latest_transaction_code.split("-")[1])
        else:
            latest_running_number = 0

        next_running_number = latest_running_number + 1
        new_transaction_code = f"{date}-{next_running_number:02}"

        # Create the new row
        new_row = {
            "account_id": account,
            "date": date,
            "transaction_code": new_transaction_code,
            "type": type.upper(),
            "amount": float(amount),
            "balance": 0.0,
        }

        # Append the new row to the DataFrame
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.df = self.df.sort_values(by=["account_id", "date", "transaction_code"]).reset_index(drop=True)

        # Recompute the account's balance
        self.compute_balance(account)

        account_balances = self.df[self.df["account_id"] == account].copy()
        account_balances.rename({"date": self.config["date_col"], "transaction_code": self.config["tansaction_col"],
                                 "type": self.config["type_col"], "amount": self.config["amount_col"]},
                                axis="columns", inplace=True)

        print(f"{self.config['account_title']}: {account}")
        print(account_balances[[self.config["date_col"], self.config["tansaction_col"], self.config["type_col"], self.config["amount_col"]]] )
        print("")

    def validate_transactions_input(self, response):
        response_list = response.split()

        if len(response_list) != 4:
            print("Please enter a valid transaction details")
        else:
            date = response_list[0]
            account = response_list[1]
            type = response_list[2].lower()
            amount = response_list[3]

            if not validate_date_format(date):
                print(f"{date} is not a valid YYYYMMdd date.")
                return False
            if type not in ['d', 'w']:
                print(f"Type is not recognized. Type is D for deposit, W for withdrawal, case insensitive")
                return False
            if not validate_amount(amount):
                print(f"{amount} is not a valid amount.")
                return False

            # Find the latest transaction_code for given account_id
            if account in self.df['account_id'].values:
                latest_transactions_balance = self.df[self.df["account_id"] == account].sort_values(by=["transaction_code"]).iloc[-1]

                if not latest_transactions_balance.empty:
                    if type == 'w':
                        new_balance = latest_transactions_balance["balance"] - float(amount)
                        if new_balance < 0:
                            print("You cannot withdraw more than your current balance.")
                            return False
            else:
                if type == 'w':
                    print("You cannot withdraw before you have a balance.")

            return True

    def transactions_input(self):
        while True:
            print(f"{self.config['transaction_input']}\n{self.config['empty_input']}")
            response = input("> ")
            # Validate response
            if response == "":
                break
            else:
                validate_success = self.validate_transactions_input(response)
                if not validate_success:
                    continue
                else:
                    # Perform insert logic
                    self.clean_transaction(*response.split())
                    break
