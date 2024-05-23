import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats

rating_col = 'Gns. rating'
# TODO: 
# Top 3 vine for hver person
# Top 10 vine totalt set
# Correlation plot
# Gns rating group by column valgt i drop down
# Correlation between wine number and rating
# Change in mean ratings over time?
# Correlation between vintage and rating

# Load the CSV file
#@st.cache_data 
#def load_data():
#    return pd.read_csv("data/ratings.csv")

#data = load_data()
data = pd.read_csv("data/ratings.csv")

data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

data.columns = data.columns.str.strip()

data["Årgang"] = pd.to_numeric(data['Årgang'], errors="coerce")

data['Dato for smagning'] = pd.to_datetime(data['Dato for smagning'], dayfirst=True)

data["Age"] = data["Dato for smagning"].dt.year - data["Årgang"]

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
exclude_cols = ["Gns. rating", "Vin nr", "Mousserende", "Jens rating", "John Rating", "Jonna rating", "Bergman rating", "Kasper rating", "Barfoed rating", "Dato for smagning"]
#data.columns.difference(exclude_cols)
exclude_cols.remove(group_by_column)
st.write(top_n.drop(columns=exclude_cols))

# Mean rating group by
st.subheader("Mean rating grouped by selected column")
exclude_cols = [rating_col, "Arrangør", "Barfoed rating", "Bergman rating", "Jonna rating", "Jens rating", "Kasper rating", "John Rating", "Flaske", "Mousserende", "Pris", "Vin nr", "Age"]
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
numeric_columns = ["Jens rating", "Bergman rating", "Jonna rating", "John Rating", "Kasper rating", "Gns. rating", "Pris", "Vin nr", "Årgang", "Age"]
st.subheader("Scatter Plot")
x_axis = st.selectbox("Select X-axis", numeric_columns)
y_axis = st.selectbox("Select Y-axis", numeric_columns)
fig, ax = plt.subplots()
sns.scatterplot(x=data[x_axis], y=data[y_axis], ax=ax)
st.pyplot(fig)

#subset = data.dropna(subset=['Age'])
##scipy.stats.pearsonr(data['Gns. rating'], data['Vin nr'])    # Pearson's r
#scipy.stats.pearsonr(subset['Gns. rating'], subset['Age'])    # Pearson's r


#data.dtypes

#data.groupby("Dato for smagning").mean("Gns. rating")