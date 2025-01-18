"""
T-test : Is there a significant difference between the first two wines and the last two wines of all tastings?
"""

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


df = pd.read_csv("data/ratings.csv")

df["Dato for smagning"] = pd.to_datetime(df["Dato for smagning"], format="%d/%m/%Y")

df = df.sort_values(by=["Dato for smagning", "Vin nr"]).reset_index(drop=True)

first_two = df.groupby("Dato for smagning").head(2)

last_two = df.groupby("Dato for smagning").tail(2)

# Perform a two-sample t-test
stat, p_value = ttest_ind(first_two["Gns. rating "], last_two["Gns. rating "])

# Interpretation
if p_value < 0.05:
    print("There is a significant difference between earlier and later wine ratings.")
else:
    print("There is no significant difference between earlier and later wine ratings.")
