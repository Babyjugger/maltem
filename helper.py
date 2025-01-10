import re
from datetime import datetime

def validate_date_format(date_string):
    try:
        # Attempt to parse the date string
        datetime.strptime(date_string, '%Y%m%d')
        return True
    except ValueError:
        # If parsing fails, the format is invalid
        return False

def validate_month_format(date_string):
    try:
        # Attempt to parse the date string
        datetime.strptime(date_string, '%Y%m')
        return True
    except ValueError:
        # If parsing fails, the format is invalid
        return False

def validate_amount(amount_string):
    # Regular expression to match a positive number with up to 2 decimal places
    pattern = r'^\d+(\.\d{1,2})?$'

    # Check if the input matches the pattern and is greater than zero
    if re.match(pattern, amount_string):
        if float(amount_string) > 0:
            return True
    return False

def validate_rate(rate_string):
    # Regular expression to match a positive number with up to 2 decimal places
    pattern = r'^\d+(\.\d{1,2})?$'

    # Check if the input matches the pattern and is greater than zero
    if re.match(pattern, rate_string):
        if float(rate_string) > 0 and float(rate_string) < 100:
            return True
    return False