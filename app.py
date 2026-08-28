import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats

rating_col = 'Gns. rating'
rater_cols = ["Jonna rating", "Bergman rating", "Barfoed rating", "Kasper rating", "Christoffer rating"]

SHEET_URL = "https://docs.google.com/spreadsheets/d/17E648xm_EVEAnR5T1L1yvaHGcwabgqNJAgmjg5klGuE/export?format=csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df.columns = df.columns.str.strip()
    df["Årgang"] = pd.to_numeric(df["Årgang"], errors="coerce")
    df["Dato for smagning"] = pd.to_datetime(df["Dato for smagning"], dayfirst=True)
    df["Age"] = df["Dato for smagning"].dt.year - df["Årgang"]
    return df

data = load_data()


# Set up the Streamlit app
st.title("CSV Data Dashboard")
st.write("This dashboard highlights some interesting aspects of the data.")

# Display the raw data
if st.checkbox("Show raw data"):
    st.subheader("Raw Data")
    st.write(data)

# Display basic statistics
#st.subheader("Basic Statistics")
#st.write(data.describe())

# Top 10 vine
st.subheader("Top n vine")
group_by_column = "Gns. rating"
user_input = st.number_input('Vis top n vine:', min_value=0, max_value=len(data), value=5, step=1, format='%d')
group_by_column = st.selectbox('Hvem vil du vise top n for?', ["Gns. rating", "Jonna rating", "Bergman rating", "Barfoed rating", "Kasper rating", "John Rating"])

top_n = data.nlargest(user_input, group_by_column)
exclude_cols = ["Gns. rating", "Vin nr", "Mousserende", "Jonna rating", "Bergman rating", "Kasper rating", "Barfoed rating", "Dato for smagning", "Christoffer rating"]
#data.columns.difference(exclude_cols)
exclude_cols.remove(group_by_column)
st.write(top_n.drop(columns=exclude_cols))

# Mean rating group by
st.subheader("Mean rating grouped by selected column")
exclude_cols = [rating_col, "Arrangør", "Barfoed rating", "Bergman rating", "Jonna rating", "Kasper rating", "Christoffer rating", "Flaske", "Mousserende", "Pris", "Vin nr", "Age"]
group_by_column = st.selectbox('Select column to group by', data.columns.difference(exclude_cols), index=2)

grouped_df = data.groupby(group_by_column)[rating_col].agg(['mean', 'std']).reset_index()

# Plotting
fig, ax = plt.subplots()
ax.bar(grouped_df[group_by_column], grouped_df['mean'], yerr=grouped_df['std'], capsize=5)
plt.xticks(rotation=90)
ax.set_xlabel(group_by_column)
ax.set_ylabel('Mean Rating')
ax.set_title(f'Mean Rating by {group_by_column}')

# Display the plot
st.pyplot(fig)

# Scatter plot for any two selected columns
numeric_columns = ["Bergman rating", "Jonna rating", "Christoffer rating", "Barfoed rating", "Kasper rating", "Gns. rating", "Pris", "Vin nr", "Årgang", "Age"]
st.subheader("Scatter Plot")
x_axis = st.selectbox("Select X-axis", numeric_columns)
y_axis = st.selectbox("Select Y-axis", numeric_columns)
fig, ax = plt.subplots()
sns.scatterplot(x=data[x_axis], y=data[y_axis], ax=ax)
st.pyplot(fig)

# --- Rater rating distributions ---
st.subheader("Rater rating distributions")
rater_numeric = data[rater_cols].apply(pd.to_numeric, errors="coerce")
melted_ratings = rater_numeric.melt(var_name="Rater", value_name="Rating").dropna()
fig, ax = plt.subplots()
sns.boxplot(data=melted_ratings, x="Rater", y="Rating", ax=ax)
ax.set_xticklabels([c.replace(" rating", "") for c in rater_cols], rotation=20, ha="right")
ax.set_xlabel("")
ax.set_ylabel("Rating")
st.pyplot(fig)

# --- Rater agreement heatmap ---
st.subheader("Rater agreement (correlation heatmap)")
corr = rater_numeric.corr()
fig, ax = plt.subplots()
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    xticklabels=[c.replace(" rating", "") for c in rater_cols],
    yticklabels=[c.replace(" rating", "") for c in rater_cols],
    ax=ax,
)
st.pyplot(fig)

# --- Mean ratings over time ---
st.subheader("Mean ratings over time")
trend_df = data[["Dato for smagning"] + rater_cols].copy()
for col in rater_cols:
    trend_df[col] = pd.to_numeric(trend_df[col], errors="coerce")
trend = trend_df.groupby("Dato for smagning")[rater_cols].mean().reset_index()
melted_trend = trend.melt(id_vars="Dato for smagning", var_name="Rater", value_name="Mean rating")
melted_trend["Rater"] = melted_trend["Rater"].str.replace(" rating", "", regex=False)
fig, ax = plt.subplots()
sns.lineplot(data=melted_trend, x="Dato for smagning", y="Mean rating", hue="Rater", marker="o", ax=ax)
plt.xticks(rotation=20, ha="right")
ax.set_xlabel("")
st.pyplot(fig)

# --- Price vs. average rating ---
st.subheader("Price vs. average rating")
price_rating = data[["Pris", rating_col]].copy()
price_rating["Pris"] = pd.to_numeric(price_rating["Pris"], errors="coerce")
price_rating[rating_col] = pd.to_numeric(price_rating[rating_col], errors="coerce")
price_rating = price_rating.dropna()
r, p = scipy.stats.pearsonr(price_rating["Pris"], price_rating[rating_col])
st.metric("Rating–Price correlation (Pearson r)", f"{r:.2f}", help=f"p-value: {p:.3f}")
x_vals = price_rating["Pris"].values
y_vals = price_rating[rating_col].values
m, b = np.polyfit(x_vals, y_vals, 1)
fig, ax = plt.subplots()
ax.scatter(x_vals, y_vals)
x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
ax.plot(x_line, m * x_line + b, color="red", linewidth=1)
ax.set_xlabel("Price")
ax.set_ylabel("Average rating")
st.pyplot(fig)

# --- Order effect (from tasting session position) ---
st.subheader("Does serving order affect ratings?")
ordered = data.sort_values(by=["Dato for smagning", "Vin nr"]).copy()
ordered[rating_col] = pd.to_numeric(ordered[rating_col], errors="coerce")
first_two = ordered.groupby("Dato for smagning").head(2)[rating_col].dropna()
last_two = ordered.groupby("Dato for smagning").tail(2)[rating_col].dropna()
stat, p_value = scipy.stats.ttest_ind(first_two, last_two)
mean1, mean2 = first_two.mean(), last_two.mean()
std1, std2 = first_two.std(ddof=1), last_two.std(ddof=1)
n1, n2 = len(first_two), len(last_two)
pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
cohens_d = (mean1 - mean2) / pooled_std
if abs(cohens_d) < 0.2:
    effect_label = "negligible"
elif abs(cohens_d) < 0.5:
    effect_label = "small"
elif abs(cohens_d) < 0.8:
    effect_label = "medium"
else:
    effect_label = "large"
col1, col2, col3 = st.columns(3)
col1.metric("Mean rating (first two wines)", f"{mean1:.1f}")
col2.metric("Mean rating (last two wines)", f"{mean2:.1f}")
col3.metric("p-value", f"{p_value:.3f}", help="Two-sample t-test, first two vs. last two wines per session")
sig = "significant" if p_value < 0.05 else "no significant"
st.write(f"{sig.capitalize()} order effect (p = {p_value:.3f}). Cohen's d = {cohens_d:.2f} ({effect_label} effect size).")

# --- Top N wines per rater ---
st.subheader("Top wines per rater")
display_cols = ["Producent", "Flaske", "Årgang", "Land"]
cols = st.columns(3)
for i, rater in enumerate(rater_cols):
    col = cols[i % 3]
    rater_data = data[[rater] + display_cols].copy()
    rater_data[rater] = pd.to_numeric(rater_data[rater], errors="coerce")
    top = rater_data.dropna(subset=[rater]).nlargest(user_input, rater).reset_index(drop=True)
    col.write(f"**{rater.replace(' rating', '')}**")
    col.dataframe(top)
