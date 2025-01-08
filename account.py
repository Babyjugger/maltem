import os
import pandas as pd

class Account:
    def __init__(self):
        filename = "data.txt"
        df = pd.read_csv(filename)

