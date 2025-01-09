import os
import pandas as pd
from helper import validate_date_format, validate_rate
from datetime import datetime

class Rule:
    def __init__(self, config):
        filename = "rule.txt"
        self.df = pd.read_csv(filename, delimiter=',', encoding="utf-8", skipinitialspace=True)
        self.config = config

    def clean_rule(self, date, rule, rate):
        # Filter transactions for the same account_id and date
        filtered_df = self.df[(self.df["date"] == date)]
        # Determine the latest running number
        if not filtered_df.empty:
            # Replace the existing rule
            self.df.loc[self.df["date"] == date, ["rule_id", "rate"]] = [rule, rate]
        else:
            # Create the new row
            new_rule = {
                "date": date,
                "rule_id": rule,
                "rate": rate,
            }
            self.df = pd.concat([self.df, pd.DataFrame([new_rule])], ignore_index=True)


        # Sort the DataFrame by date and rule_id for consistency
        self.df = self.df.sort_values(by=["date", "rule_id"]).reset_index(drop=True)
        rule_df = self.df
        rule_df.rename({"date": self.config["date_col"], "rule_id": self.config["rule_col"],
                                 "rate": self.config["rate_col"]},
                                axis="columns", inplace=True)


        print(f"{self.config['interest_rule_title']}:")
        print(rule_df)
        print("")


    def validate_rule_input(self, response):
        response_list = response.split()

        if len(response_list) != 3:
            print("Please enter a valid transaction details")
        else:
            date = response_list[0]
            rate = response_list[2]

            if not validate_date_format(date):
                print(f"{date} is not a valid YYYYMMdd date.")
                return False
            if not validate_rate(rate):
                print(f"{rate} is not a valid rate.")
                return False

            return True


    def interest_input(self):
        while True:
            print(f"{self.config['rule_input']}\n{self.config['empty_input']}")
            response = input("> ")
            # Validate response
            if response == "":
                break
            else:
                validate_success = self.validate_rule_input(response)
                if not validate_success:
                    continue
                else:
                    # Perform insert logic
                    self.clean_rule(*response.split())
                    break
