import streamlit as st
import pandas as pd
import numpy as np
import datetime

def get_return_date(df):
    return (len(df) - len(df['Full Name'].unique()))/ len(df)

st.title('Test using Etsy orders')

df_2021 = pd.read_csv('/Users/DEBORAH/Downloads/EtsySoldOrders2021 (2).csv')
df_2022 = pd.read_csv('/Users/DEBORAH/Downloads/EtsySoldOrders2022.csv')
df = pd.concat([df_2022, df_2021])

df['Sale Year'] = pd.DatetimeIndex(df['Sale Date']).year
df['Sale Date'] = pd.to_datetime(df['Sale Date'])
df['Sale Date']  = [i.date() for i in df['Sale Date']]

return_df = df[df['Full Name'].isin(df['Full Name'][df['Full Name'].duplicated()])].sort_values('Sale Date', ascending=True)

return_length = pd.DataFrame(columns = ['Name', 'Return time'])
return_length['Name'] = return_df['Full Name'].unique()

for i in return_df['Full Name'].unique():
    first_purchase = return_df[return_df['Full Name'] == i]['Sale Date'].iloc[0]
    next_purchase = return_df[return_df['Full Name'] == i]['Sale Date'].iloc[1]
    return_length.loc[return_length['Name'] == i, 'Return time'] = (next_purchase - first_purchase).days



df['Return'] = [1 if i>0 else 0 for i in df['Adjusted Net Order Amount']]


return_customer_rate = (len(df) - len(df['Full Name'].unique()))/len(df)
st.write('About {:,.1%} of customers are return customers.'.format(return_customer_rate))
st.write('On average, it takes {:,.0f} days for a customer to make another purchase.'.format(return_length['Return time'].mean()))

roll_day = 70

return_time_df = pd.DataFrame(columns = ['Start Date', 'Return rate'])
return_time_df['Start Date'] = df['Sale Date'].unique()

for i in df['Sale Date'].unique():
    end_date = i + datetime.timedelta(days=roll_day)
    df_subset = df.loc[(df['Sale Date'] >= i) & (df['Sale Date'] <= end_date), :]
    return_time_df.loc[return_time_df['Start Date'] == i, 'Return rate'] = get_return_date(df_subset)

st.line_chart(return_time_df[return_time_df['Start Date'] <= (return_time_df['Start Date'].max() - datetime.timedelta(days=roll_day))].set_index('Start Date'))

return_item_rate = len(df[df['Adjusted Net Order Amount'] > 0]) / len(df)

st.write('About {:,.1%} of customers are returning their products.'.format(return_item_rate))

pvt = df.pivot_table(index = 'Sale Year', values = ['Return', 'Order ID'], aggfunc = {'Return': np.sum, 'Order ID': len})

pvt['Return rate'] = pvt['Return'] / pvt['Order ID']
st.write(pvt.style.format({'Return rate': '{:.1%}'}))

