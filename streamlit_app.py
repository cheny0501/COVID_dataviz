import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###


@st.cache_data
def load_data():
    df1 = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-2021.csv")
    df_vac = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv")
    
    # start from 2021-01-12
    df1 = df1[df1['date'] > '2021-01-11']
    # groupby cases and deaths for same date
    df1 = df1.groupby(['date','state']).agg({'cases': 'sum', 'deaths': 'sum'})
    df_vac = df_vac[[ "date", "location","total_vaccinations", "total_vaccinations_per_hundred" ]]
    df_vac = df_vac.rename(columns={"location": "state"})
    df_new = df1.merge(df_vac, on=['date', 'state'], how='left')
    df_new.dropna(inplace=True)
    df["date"] = pd.to_datetime(df["date"]).astype(int) / 10**9 
    return df


# Uncomment the next line when finished
df = load_data()

### P1.2 ###


st.write("## Geographical Distribution")

### P2.1 ###

# replace with st.slider
date = st.slider("date", int(df["date"].min()), int(df["date"].max()), int(df["date"].min()))
subset = df[df["date"] == date]
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex = st.radio("Sex", ("M", "F"))
subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
default = [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
]
countries = st.multiselect('Countries', subset["Country"].unique(), default)
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer_options = df["Cancer"].unique()
cancer = st.selectbox("Cancers", cancer_options)
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

chart = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y("Country"),
    color=alt.Color("Rate", scale=alt.Scale(type='log',domain=(0.01,1000),clamp=True), legend=alt.Legend(title="Mortality rate per 100k")),
    tooltip=["Rate"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)

### P2.5 ###

st.altair_chart(chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
