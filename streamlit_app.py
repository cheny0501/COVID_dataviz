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
    df1["date"] = pd.to_datetime(df["date"]).astype(int) / 10**9 
    # Group the data by state and date
    grouped = df1.groupby(['state', 'date'])
    # Calculate the mortality rate for each state and date
    mortality_rates = (grouped['deaths'].sum() / grouped['cases'].sum()) * 100
    # Add the mortality rates as a new column to the original DataFrame
    df1['case_fatality_rate'] = df1.set_index(['state', 'date']).index.map(mortality_rates.get)
    df_wide = df1
    
    return df_wide

df_wide = load_data1()

@st.cache_data
def load_data2():
# change df to long
    df_long = df1.melt(id_vars=['date', 'state'], value_vars=['cases', 'deaths', 'total_vaccinations', 'total_vaccinations_per_hundred', 'mortality'], var_name='selection')
    
    return df_long

df_long = load_data2()    

def load_data3():
  task1_df = df_long[df_long['selection'].isin(['cases', 'deaths'])]
  return task1_df

task1_df = load_data3()    
