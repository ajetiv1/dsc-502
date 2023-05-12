import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

#raw data
df_flights = pd.read_csv('./dataset/flights-abr.csv')
df_aiports = pd.read_csv('./dataset/airports1.csv')

#Cleaning raw data, taking columns MONTH and DAY and covert into a date type 
df_date = df_flights.loc[:,'MONTH':'DAY']
df_date['YEAR'] = 2015
df_date['MONTH'] = df_date['MONTH'].apply(lambda x: '{0:0>2}'.format(x))
df_date['DAY'] = df_date['DAY'].apply(lambda x: '{0:0>2}'.format(x))
df_date = df_date.applymap(str)
df_date['DATE_S'] = df_date['DAY']+ df_date['MONTH'] + df_date['YEAR']
df_date['DATE'] = pd.to_datetime(df_date['DATE_S'], format='%d%m%Y')

#Date part of dataframe that with be merged with other dataframes
df_date2 = df_date.loc[:,'DATE']

#converting NaN to zeros for delay times
df_delays = df_flights.loc[:,'AIR_SYSTEM_DELAY':'WEATHER_DELAY']
df_delays = df_delays.fillna(0)
df_delays['TOTAL_DELAY'] = df_delays.sum(axis=1)
df_delays = df_delays.astype('int')

#marging all the parts of the dataframes into one final dataframe with date and
#fixed NaN values
df3 = df_flights.loc[:,'DAY_OF_WEEK':'CANCELLATION_REASON']
df_final = pd.concat([df_date2, df3, df_delays], axis=1, join='inner')


st.title('US Domestic Flights in 2015: January - March')

tab1, tab2, tab3 = st.tabs(["Final Data", "Raw Data","Map of Airports"])

with tab1:
   st.write(df_final)

with tab2:
   st.write(df_flights)

with tab3:
	data1 = df_aiports.loc[:,'LATITUDE':'LONGITUDE']
	st.map(data1)   

st.subheader('Flight Delays by Delay Type')

delay_cat = st.radio('Category of Delays', ('Air System Delay', 'Security Delay', 'Airline Delay', 'Late Aircraft Delay', 'Total Delay'))
delay_type = 'TOTAL_DELAY'

if delay_cat == 'Air System Delay':
	delay_type = 'AIR_SYSTEM_DELAY' 
	df_dlt = df_delays.loc[df_delays[delay_type]>0]
elif delay_cat == 'Security Delay':
	delay_type = 'SECURITY_DELAY' 
	df_dlt = df_delays.loc[df_delays[delay_type]>0]
elif delay_cat == 'Airline Delay':
	delay_type = 'AIRLINE_DELAY'
	df_dlt = df_delays.loc[df_delays[delay_type]>0]
elif delay_cat == 'Late Aircraft Delay':
	delay_type = 'LATE_AIRCRAFT_DELAY'
	df_dlt = df_delays.loc[df_delays[delay_type]>0]
else:
	delay_type = 'TOTAL_DELAY'
	df_dlt = df_delays.loc[df_delays[delay_type]>0]

fig = plt.figure()
ax = fig.add_subplot()
ax.set_xlabel('Delay in Minutes')
ax.set_ylabel('Number of')
ax.hist(df_dlt[delay_type], range=[10, 120], bins=19 )
st.pyplot(fig)


#df for canceled flights and the canelation reason
df_canceled = df_final.loc[df_final['CANCELLED'] == 1, ['DATE','DAY_OF_WEEK','AIRLINE','ORIGIN_AIRPORT','DESTINATION_AIRPORT','CANCELLATION_REASON']]

#df for diverted flights
df_diverted = df_final.loc[df_final['DIVERTED'] == 1, ['DATE','DAY_OF_WEEK','AIRLINE','ORIGIN_AIRPORT','DESTINATION_AIRPORT']]

#df for delayed flights for any reason
df_delayed = df_final.loc[df_final['TOTAL_DELAY'] > 0]


st.subheader('Flights Delayed, Canceled or Diverted by Date')


chart_data = pd.DataFrame({
    "Canceled": df_canceled['DATE'].value_counts(),
    "Diverted": df_diverted['DATE'].value_counts(),
    "Delayed": df_delayed['DATE'].value_counts()})

st.line_chart(chart_data)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
	d = st.date_input(
    "Date",
    datetime.date(2015, 1, 1))
	
	ds = d.strftime("%m/%d/%Y %H:%M:%S")
	st.write(d)

with col2:
	xv1 = chart_data.at[ds,'Delayed']
	st.metric(label="Flights Delayed", value=xv1)

with col3:
	xv2 = chart_data.at[ds,'Canceled']
	st.metric(label="Flights Canceled", value=xv2)

with col4:
	xv3 = chart_data.at[ds,'Diverted']
	st.metric(label="Flights Diverted", value=xv3)

st.subheader('Airline Delays')

df_a1 = pd.read_csv('./dataset/airlines.csv')
df_a2 = pd.DataFrame()
df_a2['IATA_CODE'] = df_delayed['AIRLINE']
df_a3 = df_a2.merge(df_a1, on='IATA_CODE')


bar_data = pd.DataFrame(df_a3['AIRLINE'].value_counts())
st.bar_chart(bar_data)


st.subheader('Airline Cancellations')

df_c1 = pd.read_csv('./dataset/airlines.csv')
df_c2 = pd.DataFrame()
df_c2['IATA_CODE'] = df_canceled['AIRLINE']
df_c3 = df_c2.merge(df_c1, on='IATA_CODE')

bar_data = pd.DataFrame(df_c3['AIRLINE'].value_counts())
st.bar_chart(bar_data)

st.subheader('Reason for Cancellation of Flight')

labels = 'Weather', 'Airline/Carrier', 'National Air System', 'Security'
explode = (0.1, 0.1, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots()
ax1.pie(df_canceled['CANCELLATION_REASON'].value_counts(), explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

st.pyplot(fig1)