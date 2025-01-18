"""
T-test : Is there a significant difference between the first two wines and the last two wines of all tastings?
"""

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


df = pd.read_csv("data/ratings.csv")

df["Dato for smagning"] = pd.to_datetime(df["Dato for smagning"], format="%d/%m/%Y")

df = df.sort_values(by=["Dato for smagning", "Vin nr"]).reset_index(drop=True)

first_two = df.groupby("Dato for smagning").head(2)["Gns. rating "]

last_two = df.groupby("Dato for smagning").tail(2)["Gns. rating "]

# Perform a two-sample t-test
stat, p_value = ttest_ind(first_two, last_two)

# Interpretation
if p_value < 0.05:
    print("There is a significant difference between earlier and later wine ratings.")
else:
    print("There is no significant difference between earlier and later wine ratings.")

## >>> There is no significant difference between earlier and later wine ratings.


import numpy as np

# Calculate group statistics
mean1, mean2 = np.mean(first_two), np.mean(last_two)
std1, std2 = np.std(first_two, ddof=1), np.std(last_two, ddof=1)
n1, n2 = len(first_two), len(last_two)

# Calculate pooled standard deviation
pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

# Calculate Cohen's d
cohens_d = (mean1 - mean2) / pooled_std

# Output the results
print(f"Mean (First Two Wines): {mean1:.2f}")
print(f"Mean (Last Two Wines): {mean2:.2f}")
print(f"Pooled Standard Deviation: {pooled_std:.2f}")
print(f"Cohen's d: {cohens_d:.2f}")

# Interpretation
if abs(cohens_d) < 0.2:
    effect_size_interpretation = "negligible"
elif abs(cohens_d) < 0.5:
    effect_size_interpretation = "small"
elif abs(cohens_d) < 0.8:
    effect_size_interpretation = "medium"
else:
    effect_size_interpretation = "large"

print(f"Effect size interpretation: {effect_size_interpretation}")
### Effect size interpretation: small