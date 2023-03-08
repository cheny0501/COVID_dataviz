import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

alt.data_transformers.disable_max_rows()

# Data pre-processing and load data

@st.cache
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
    # change new york
    df_vac['state'] = df_vac['state'].str.replace('New York State', 'New York')
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
    state_abbreviations = {
    'Alabama': '1', 'Alaska': '2', 'Arizona': '4', 'Arkansas': '5', 'California': '6', 
    'Colorado': '8', 'Connecticut': '9', 'Delaware': '10', 'District of Columbia':'11', 'Florida': '12', 'Georgia': '13', 
    'Hawaii': '15', 'Idaho': '16', 'Illinois': '17', 'Indiana': '18', 'Iowa': '19', 
    'Kansas': '20', 'Kentucky': '21', 'Louisiana': '22', 'Maine': '23', 'Maryland': '24', 
    'Massachusetts': '25', 'Michigan': '26', 'Minnesota': '27', 'Mississippi': '28', 
    'Missouri': '29', 'Montana': '30', 'Nebraska': '31', 'Nevada': '32', 'New Hampshire': '33', 
    'New Jersey': '34', 'New Mexico': '35', 'New York': '36', 'North Carolina': '37', 
    'North Dakota': '38', 'Ohio': '39', 'Oklahoma': '40', 'Oregon': '41', 'Pennsylvania': '42', 
    'Rhode Island': '44', 'South Carolina': '45', 'South Dakota': '46', 'Tennessee': '47', 
    'Texas': '48', 'Utah': '49', 'Vermont': '50', 'Virginia': '51', 'Washington': '53', 
    'West Virginia': '54', 'Wisconsin': '55', 'Wyoming': '56', "Puerto Rico":'72'
    }

    # Use the dictionary to create a new column with the state abbreviations
    df_wide['id'] = df_wide['state'].map(state_abbreviations)
    
    return df_wide

df_wide = load_data1()

def load_data2():
# change df to long
    df_long = df_wide.melt(id_vars=['date', 'state'], value_vars=['cases', 'deaths', 'total_vaccinations', 'total_vaccinations_per_hundred', 'case_fatality_rate'], var_name='selection')
    
    return df_long

df_long = load_data2()    

def load_data3():
  task1_df = df_long[df_long['selection'].isin(['cases', 'deaths'])]
  return task1_df

task1_df = load_data3()   

def load_data4():
    source = alt.topo_feature(data.us_10m.url, "states")
    return source

source = load_data4()  

### Title ###

st.write("## Visualizing the Impact of COVID-19")
st.write("#### Group: Viz or DY")
st.write("#### Tony Ding, Chen Yang")

#### Task1 ###
st.write("#### Task1: What’s the trend of COVID-19 cases and deaths over time in the US?")
# Create the chart
chart = alt.Chart(task1_df).mark_area(color = 'green',
                           opacity = 0.5,
                           line = {'color':'darkgreen'}).encode(
    x='date:T',
    y="value:Q",
    color="selection:N",
    row="selection:N",
    tooltip=["date:T", "value:Q"]
).resolve_scale(y='independent')

# Render the chart using the altair renderer
st.altair_chart(chart)

#### Task2 ####

st.write("#### Task2: How do vaccinations administered total/per state/per region impact the spread of COVID-19?")
# create a drop-down state selector
state = st.selectbox("Please select a state:",df_wide['state'].unique())
subset = df_wide[df_wide["state"] == state]

#state_dropdown = alt.binding_select(options=state)
#state_select = alt.selection_single(fields=['state'], bind=state_dropdown, name="state",init={'state':'Alabama'})

# case fatality rate over the year of 2021
base = alt.Chart(subset).properties(
    width=650
).encode(
  x=alt.X('date:T', axis=alt.Axis(title='Date')),
  y=alt.Y('case_fatality_rate',axis=alt.Axis(title='Case Fatality Rate')),
  color='state'
).properties(
    title='Case Fatality rate over the year of 2021'
)

# base for total Vaccinations over 2021
base_2 = alt.Chart(subset).properties(
    width=650
).encode(
  x=alt.X('date:T', axis=alt.Axis(title='Date')),
  y=alt.Y('total_vaccinations:Q', axis=alt.Axis(title='Total Vaccinations')),
  color='state'
).properties(
    title='Total Vaccinations over the year of 2021'
)

# add brush
brush = alt.selection_interval(encodings=['x'])

upper = base.mark_line(point=True).encode(
    alt.X('date:T',scale=alt.Scale(domain=brush),axis=alt.Axis(title='Date')),
    y =alt.Y('case_fatality_rate:Q',axis=alt.Axis(title='Case Fatality Rate')),
    color = 'state',
    tooltip = ["date:T","case_fatality_rate:Q"]
).transform_filter(
    brush
)

lower = base_2.add_selection(
    brush
).mark_bar()

lower = lower.properties(
    height=50
)

chart1 = upper & lower
st.altair_chart(chart1)

### Task 3 & 4 ###

st.write("### How does COVID-19’s geographical distribution regarding cases and deaths differ among states? How do the vaccination statuses vary among states?")

# replace with st.slider
df_wide['date'] = pd.to_datetime(df_wide['date'])
date_selection = st.date_input("Date", min_value=df_wide["date"].min(), max_value=df_wide["date"].max(), value=df_wide["date"].min())
subset = df_wide[df_wide["date"] == date_selection]

start_time = st.slider(
    "When do you start?",
    value=datetime(2021, 1, 12, 9, 30),
    max_value = datetime(2021,12,30,23,59),
    format="MM/DD/YY - hh:mm")
st.write("Start time:", start_time)

width = 600
height  = 300
project = 'albersUsa'

# a gray map using as the visualization background
background = alt.Chart(source
).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

selector = alt.selection_single(
    on='click'
    )

chart_base = alt.Chart(source
    ).properties( 
        width=width,
        height=height
    ).project(project
    ).add_selection(selector
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(subset, "id", ['case_fatality_rate','state','date','total_vaccinations','total_vaccinations_per_hundred','cases','deaths']),
    )

rate_scale = alt.Scale(domain=[df_wide['case_fatality_rate'].max(), df_wide['case_fatality_rate'].min()], scheme='inferno')
rate_color = alt.Color(field="case_fatality_rate", type="quantitative", scale=rate_scale)
vac_scale = alt.Scale(domain=[df_wide['total_vaccinations_per_hundred'].max(), df_wide['total_vaccinations_per_hundred'].min()], scheme='Viridis')
vac_color = alt.Color(field="total_vaccinations_per_hundred", type="quantitative", scale=vac_scale)

chart_rate = chart_base.mark_geoshape().encode(
    color=rate_color,
    tooltip=['case_fatality_rate:Q', 'state:N','cases:Q','deaths:Q']
    ).transform_filter(
    selector
    )
   
chart_vac = chart_base.mark_geoshape().encode(
    color=vac_color,
    tooltip=['total_vaccinations_per_hundred:Q','state:N']
    ).transform_filter(
    selector
    )

chart2 = alt.vconcat(background + chart_rate, background + chart_vac
).resolve_scale(
    color='independent'
)
st.altair_chart(chart2)
