import altair as alt
import pandas as pd
import streamlit as st

# Data pre-processing

@st.cache_data
def load_data1():
    # read data
    df_case = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-2021.csv")
    df_vac = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv")
    
    # start from 2021-01-12
    # since the record for df_vac began from 2021-01-12
    df_case = df_case[df_case['date'] > '2021-01-11']
    # groupby cases and deaths for same date
    df_case = df_case.groupby(['date','state']).agg({'cases': 'sum', 'deaths': 'sum'})
    # subset only useful columns
    df_vac = df_vac[[ "date", "location","total_vaccinations", "total_vaccinations_per_hundred" ]]
    # rename to be consistent for merging
    df_vac = df_vac.rename(columns={"location": "state"})
    # merge the two datasets
    df1 = df_case.merge(df_vac, on=['date', 'state'], how='left')
    # drop all missing values
    df1.dropna(inplace=True)
    # change date type
    df1["date"] = pd.to_datetime(df1["date"])
    # Group the data by state and date
    grouped = df1.groupby(['state', 'date'])
    # Calculate the mortality rate for each state and date
    case_fatality_rate = (grouped['deaths'].sum() / grouped['cases'].sum()) * 100
    # Add the mortality rates as a new column to the original DataFrame
    df1['case_fatality_rate'] = df1.set_index(['state', 'date']).index.map(case_fatality_rate.get)
    df_wide = df1
    
    return df_wide

df_wide = load_data1()

@st.cache_data
def load_data2():
# change df to long
    df_long = df_wide.melt(id_vars=['date', 'state'], value_vars=['cases', 'deaths', 'total_vaccinations', 'total_vaccinations_per_hundred', 'case_fatality_rate'], var_name='selection')
    
    return df_long

df_long = load_data2()    

def load_data3():
  task1_df = df_long[df_long['selection'].isin(['cases', 'deaths'])]
  return task1_df

task1_df = load_data3()    

### Title ###

st.write("## Visualizing the Impact of COVID-19")
st.write("#### Group: Viz or DY")
st.write("#### Tony Ding, Chen Yang")

#### Task1 ###
st.write("#### Task1: What’s the trend of COVID-19 cases and deaths over time in the US?")
# Create the chart
chart = alt.Chart(task1_df).mark_line().encode(
    x='date:T',
    y="value:Q",
    color="selection:N",
    row="selection:N",
    tooltip=["date:T", "value:Q"]
).resolve_scale(y='independent')

# Render the chart using the altair renderer
st.altair_chart(chart, use_container_width=True)

#### Task2 ###

st.write("Task 2")

# create a drop-down cancer selector
state = st.selectbox("Please select a state:",df_wide['state'].unique())
subset = df_wide[df_wide["state"] == state]

#state_dropdown = alt.binding_select(options=state)
#state_select = alt.selection_single(fields=['state'], bind=state_dropdown, name="state",init={'state':'Alabama'})


base = alt.Chart(subset).properties(
    width=650
).encode(
  x='date:T',
  y='case_fatality_rate',
  color='state'
).properties(
    title='Case Fatality rate over the year of 2021'
)


base_2 = alt.Chart(subset).properties(
    width=650
).encode(
  x='date:T',
  y='total_vaccinations',
  color='state'
).properties(
    title='Total Vaccinations over the year of 2021'
)

########################
# add brush
brush = alt.selection_interval(encodings=['x'])

# add your code here
upper = base.mark_line(point=True).encode(
    alt.X('date:T',scale=alt.Scale(domain=brush)),
    y = 'case_fatality_rate:Q',
    color = 'state',
    tooltip = ["date:T","case_fatality_rate:Q"]
).transform_filter(
    brush
)

# add your code here
lower = base_2.add_selection(
    brush
).mark_bar()

lower = lower.properties(
    height=50
)

chart1 = upper & lower
st.altair_chart(chart1)


