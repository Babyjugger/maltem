import pandas as pd
from datetime import datetime, timedelta
from helper import validate_month_format

class ComputeTransaction:
    def __init__(self, config):
        self.config = config
        self.account_df = None
        self.interest_rules_df = None


    def validate_input(self, response, account_df):
        response_list = response.split()

        if len(response_list) != 2:
            print("Please enter a valid account and month")
            return False
        else:
            account_id = response_list[0]
            month = response_list[1]

            filter_account_df = account_df[account_df["account_id"] == account_id]
            if filter_account_df.empty:
                print(f"Account {account_id} not found.")
                return False

            if not validate_month_format(month):
                print(f"{month} is not a valid YYYYMM date.")
                return False

        return True

    def _compute_monthly_interest(self, transactions, month):
        applicable_rules = self.interest_rules_df.copy()
        monthly_interest = 0.0

        month_start = pd.to_datetime(f"{month}01", format="%Y%m%d")
        month_end = (month_start + pd.offsets.MonthEnd(0)).strftime("%Y%m%d")
        month_start = month_start.strftime("%Y%m%d")

        # Get previous month interest if exist
        previous_month_interest = applicable_rules[(applicable_rules["date"] < pd.to_datetime(month_start, format="%Y%m%d"))].sort_values(
            by=["date"]).tail(1).reset_index(drop=True)
        previous_month_interest.loc[0, "date"] = month_start

        selected_month_rule_df = applicable_rules[
            (applicable_rules["date"] >= pd.to_datetime(month_start, format="%Y%m%d")) &
            (applicable_rules["date"] <= pd.to_datetime(month_end, format="%Y%m%d"))
            ]

        new_interest_rate_df = selected_month_rule_df.reset_index(drop=True)

        if not previous_month_interest.empty:
            new_interest_rate_df = pd.concat([previous_month_interest, selected_month_rule_df], ignore_index=True).reset_index(drop=True)

        new_interest_rate_df["date"] = pd.to_datetime(new_interest_rate_df["date"])
        new_interest_rate_df = new_interest_rate_df.sort_values(by="date").reset_index(drop=True)

        # Prepare the rules with end dates
        new_interest_rate_df["end_date"] = new_interest_rate_df["date"].shift(-1)
        new_interest_rate_df.iloc[-1, new_interest_rate_df.columns.get_loc("end_date")] = pd.to_datetime(month_end)

        # Iterate through each rule period
        for _, rule in new_interest_rate_df.iterrows():

            start_date = rule["date"]
            end_date = rule["end_date"]

            # There will have 2 cases, 1 is update the rate another is update the transaction

            # Fetch balance for the period
            period_balance = transactions[
                (transactions["date"] >= start_date) & (transactions["date"] < end_date)
                ]["balance"].max() if not transactions.empty else 0.0





            # Default to the last balance if no transaction occurred
            if pd.isna(period_balance):
                period_balance = transactions["balance"].iloc[-1] if not transactions.empty else 0.0

            # Calculate interest for the period
            days = (end_date - start_date).days
            rate = rule["rate"] / 100  # Convert percentage to fraction
            monthly_interest += period_balance * rate * days

        return round(monthly_interest, 2)

    def _process_account_transactions(self, account_data, month):
        """
        Process transactions for a single account and compute monthly interest.
        """
        processed = []
        balance = 0.0
        month_start = pd.to_datetime(f"{month}01", format="%Y%m%d")
        month_end = (month_start + pd.offsets.MonthEnd(0)).strftime("%Y%m%d")

        # Iterate through transactions
        for i, row in account_data.iterrows():
            # Add transaction to processed list
            processed.append({
                "date": row["date"].strftime("%Y%m%d"),
                "transaction_code": row["transaction_code"],
                "type": row["type"],
                "amount": f"{row['amount']:.2f}",
                "balance": f"{row['balance']:.2f}",
            })

        # Add interest row at the end of the month
        monthly_interest = self._compute_monthly_interest(account_data, month)
        if monthly_interest > 0:
            processed.append({
                "date": month_end,
                "transaction_code": "",
                "type": "I",
                "amount": f"{monthly_interest:.2f}",
                "balance": f"{balance + monthly_interest:.2f}",
            })

        return processed

    def _compute_transactions_with_interest(self, month_end):
        results = []
        last_balance = 0.0
        last_date = None
        interest_accumulated = 0.0

        # Prepare interest rules with end dates
        self.interest_rules_df["end_date"] = self.interest_rules_df["date"].shift(-1)
        self.interest_rules_df.iloc[-1, self.interest_rules_df.columns.get_loc("end_date")] = self.last_day_of_month

        for i, txn in self.account_df.iterrows():
            txn_date = txn["date"]
            txn_amount = txn["amount"]
            txn_type = txn["type"]
            txn_balance = txn["balance"]

            # Apply interest for gaps between last_date and txn_date
            if last_date is not None and txn_date > last_date:
                interest_accumulated += self._apply_interest_for_gap(last_date, txn_date, last_balance)

            if last_date is not None:
                # Update balance based on transaction type
                if txn_type == "D":  # Deposit
                    last_balance += txn_amount
                elif txn_type == "W":  # Withdrawal
                    last_balance -= txn_amount
            else:
                last_balance = txn_balance

            # Record the transaction
            results.append({
                "Date": txn_date.strftime("%Y%m%d"),
                "Txn Id": txn["transaction_code"],
                "Type": txn_type,
                "Amount": f"{txn_amount:.2f}",
                "Balance": f"{txn_balance:.2f}",
            })
            last_date = txn_date

        # Apply interest for the remaining period in the month
        interest_accumulated += self._apply_interest_for_gap(last_date - timedelta(days=1), datetime.strptime(month_end, '%Y%m%d'), last_balance)

        # Add interest row if applicable
        if interest_accumulated > 0:
            results.append({
                "Date": month_end,
                "Txn Id": "",
                "Type": "I",
                "Amount": f"{interest_accumulated:.2f}",
                "Balance": f"{last_balance + interest_accumulated:.2f}",
            })

        return pd.DataFrame(results)

    def _apply_interest_for_gap(self, start_date, end_date, balance):
        """
        Calculate interest for the period between start_date and end_date.
        """

        applicable_rules = self.interest_rules_df[
            (self.interest_rules_df["date"] <= end_date) & (self.interest_rules_df["end_date"] > start_date)
            ]

        interest = 0.0
        for _, rule in applicable_rules.iterrows():
            period_start = max(start_date, rule["date"])
            period_end = min(end_date, rule["end_date"])
            days = (period_end - period_start).days
            rate = rule["rate"] / 100  # Convert percentage to decimal

            # Calculate interest for this period
            interest += balance * rate * days

        return round(interest  / 365 , 2)


    def preprocess(self, account_id, month):
        # Filter by account_id and month if provided

        self.account_df = self.account_df[self.account_df["account_id"] == account_id]
        month_start = pd.to_datetime(f"{month}01", format="%Y%m%d")
        month_end = (month_start + pd.offsets.MonthEnd(0)).strftime("%Y%m%d")
        month_start = month_start.strftime("%Y%m%d")

        self.account_df = self.account_df[
            (self.account_df["date"] >= pd.to_datetime(month_start, format="%Y%m%d")) &
            (self.account_df["date"] <= pd.to_datetime(month_end, format="%Y%m%d"))
        ]
        self.last_day_of_month = month_end

        # Sort account_df by transaction_code and interest_rules_df by date
        self.account_df = self.account_df.sort_values(by="transaction_code").reset_index(drop=True)
        self.interest_rules_df = self.interest_rules_df.sort_values(by="date").reset_index(drop=True)

        # Process transactions for the filtered data
        return self._compute_transactions_with_interest(month_end)


    def print_input(self, account, rule):
        # Ensure 'date' columns are in datetime format
        account.df["date"] = pd.to_datetime(account.df["date"], format="%Y%m%d")
        rule.df["date"] = pd.to_datetime(rule.df["date"], format="%Y%m%d")

        while True:
            print(f"{self.config['print_input']}\n{self.config['empty_input']}")
            response = input("> ")
            if response == "":
                break
            else:
                validate_success = self.validate_input(response, account.df)
                if not validate_success:
                    continue
                else:
                    self.account_df = account.df.copy()
                    self.interest_rules_df = rule.df.copy()
                    result_df = self.preprocess(*response.split())
                    print(result_df)
                    break
