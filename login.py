import pandas as pd
import numpy as np
import streamlit as st
import pyodbc
import plotly.express as px
import random
import warnings

warnings.filterwarnings('ignore')

server_name = '172.25.35.150'
database_name = 'EFatura'


st.set_page_config(layout="wide")

if 'username' not in st.session_state:
    st.session_state['username'] = ''
    
if 'username_2' not in st.session_state:
    st.session_state['username_2'] = ''

if 'password' not in st.session_state:
    st.session_state['password'] = ''
    
if 'password_2' not in st.session_state:
    st.session_state['password_2'] = ''
    
if 'counter1_value' not in st.session_state:
    st.session_state['counter1_value'] = 0

if 'start_date' not in st.session_state:
     st.session_state['start_date'] = pd.to_datetime('1900-01-01')

if 'start_date_2' not in st.session_state:
     st.session_state['start_date_2'] = pd.to_datetime('1900-01-01')

if 'end_date' not in st.session_state:
     st.session_state['end_date'] = pd.to_datetime('2023-09-01')

if 'end_date_2' not in st.session_state:
     st.session_state['end_date_2'] = pd.to_datetime('2023-09-01')

if 'start_date_min' not in st.session_state:
     st.session_state['start_date_min'] = pd.to_datetime('1900-01-01')

if 'end_date_max' not in st.session_state:
     st.session_state['end_date_max'] = pd.to_datetime('2023-09-01')

#if 'firma_selected' not in st.session_state:
    #st.session_state['firma_selected'] = ''

#if 'firma_selected_2' not in st.session_state:
    #st.session_state['firma_selected_2'] = ''

def login_callback():
    st.session_state['counter1_value'] += 1

    
def login_another_callback():

    st.session_state['username'] = st.session_state['username_2']
    st.session_state['password'] = st.session_state['password_2']
    st.session_state['counter1_value'] = 0


def start_date_callback():
    global start_date
    global end_date
    start_date = pd.to_datetime(st.session_state['start_date_2'])
    end_date = pd.to_datetime(st.session_state['end_date_2'])
    
def end_date_callback():
    global start_date
    global end_date
    start_date = pd.to_datetime(st.session_state['start_date_2'])
    end_date = pd.to_datetime(st.session_state['end_date_2'])

def refresh_callback():
     global start_date
     global end_date
     start_date = st.session_state['start_date']
     end_date = st.session_state['end_date']

def all_dates_callback():
     global start_date
     global end_date
     start_date = st.session_state['start_date_min']
     end_date = st.session_state['end_date_max']
     st.session_state['start_date'] = start_date
     st.session_state['end_date'] = end_date

    
#def firma_selected_callback():
    #st.session_state['firma_selected'] = st.session_state['firma_selected_2']



    
def login_page():
    st.title('Login Page')
    st.write(f'Lutfen {server_name} adli server daki {database_name} adli database e erismek icin kullanidiginiz username ve password u girin')
    st.write('\n')
    
    username_input = st.text_input('Username', key='username', value=st.session_state['username_2'])
    password_input = st.text_input('Password', type='password', key='password', value=st.session_state['password_2'])
    st.write('\n')
    
    st.button('Login', key = 'login_button_value', on_click=login_callback)
    
    st.session_state['username_2'] = username_input
    st.session_state['password_2'] = password_input
    
    return st.session_state['username_2'], st.session_state['password_2']
    

col1, col2, col3 = st.columns([0.65, 1, 0.65])

try:
    
    for i in range(4):
        st.write('\n')
    
    if st.session_state['counter1_value'] == 0:
        with col2:
        
            st.session_state['username_2'] , st.session_state['password_2'] = login_page()
        
    else:
        
        server = server_name
        database = database_name
        username_db = st.session_state['username_2']
        password_db = st.session_state['password_2']

        connection = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username_db};PWD={password_db};timeout=30')

        coli1, coli0, coli01, coli02, coli2, coli3 = st.columns([2,3,1,1,8,2])

        with coli2:
             
            st.image("https://mukayese.com/img/internet-providers/isnet.png", width=200)
        
        col4, col5, col55, col65, col6 = st.columns([1, 1, 2.5, 1 ,0.31])

        with col55:
             st.title('Tarihe Gore Fatura Kesimler')

        with col4:
        
            login_another_input = st.button('Login with Another Account', key = 'login_another_value', on_click=login_another_callback)

        with col6:
            for i in range(1):
                 st.write('\n')
            st.button('Refresh', on_click=refresh_callback)


        firmalar_query2 = f'''
                                select a.ID_FIRMA, b.FIRMA_ADI from DCOMMON.ST_FATURA a left join GN_FIRMA b on a.ID_FIRMA = b.ID_FIRMA
                                '''
            
        firmalar0 = pd.read_sql(firmalar_query2, connection)
        firmalar1 = firmalar0['FIRMA_ADI'].unique()

        firma_selected_input = st.multiselect('Bakmak istediginiz firmalari secin', firmalar1, default='900-SYS')


        firmalar = ', '.join([f"'{val}'" for val in firma_selected_input])
        firmalar_parantez = f'({firmalar})'
        
        query = f"""
                        select 
                        a.ID_FIRMA,
                        a.FATURA_TARIHI,
                        a.KAYIT_TARIHI,
                        a.TOPLAM_TUTAR,
                        g.FIRMA_ADI
                        from(
                        select
                                    sf.ID_FIRMA,
                                    convert(DATE, sf.FATURA_TARIHI) as FATURA_TARIHI,
                                    count(*) as KAYIT_TARIHI,
                                    sum(sf.ODENECEK_TUTAR) as TOPLAM_TUTAR
                        from DCOMMON.ST_FATURA sf
                        group by sf.ID_FIRMA, convert(DATE, sf.FATURA_TARIHI)
                            )a
                        left join GN_FIRMA g on a.ID_FIRMA = g.ID_FIRMA
                        where g.FIRMA_ADI in {firmalar_parantez};
                        
                    """
        df = pd.read_sql(query, connection)

        df['FATURA_TARIHI'] = pd.to_datetime(df['FATURA_TARIHI'])

        st.session_state['start_date_min'] = df['FATURA_TARIHI'].min()
        st.session_state['end_date_max'] = df['FATURA_TARIHI'].max()

        df1 = df.copy()
        col7, col8, col9 = st.columns([1,1,0.2])

        with col7:

            start_date = pd.to_datetime(st.date_input('Baslangic Tarihi', min_value = df1['FATURA_TARIHI'].min(), max_value=df1['FATURA_TARIHI'].max(), value = df1['FATURA_TARIHI'].min(), key='start_date'))
            start_date_callback()  
  
        with col8:

            end_date = pd.to_datetime(st.date_input('Bitis Tarihi', min_value=start_date+pd.DateOffset(days=1), max_value=df1['FATURA_TARIHI'].max(), value = df1['FATURA_TARIHI'].max(), key='end_date'))
            end_date_callback()  


        with col9:
            for i in range(2):
                 st.write('\n')

            all_dates_button = st.button('See All Dates', on_click=all_dates_callback)

            if all_dates_button:
                  start_date = st.session_state['start_date_min']
                  end_date = st.session_state['end_date_max']

        df2 = df1[(df1['FATURA_TARIHI']>=pd.to_datetime(st.session_state['start_date'])) & (df1['FATURA_TARIHI']<=pd.to_datetime(st.session_state['end_date']))]

        df2['KAYIT_TARIHI'] = df2['KAYIT_TARIHI'].astype(float)

        df2 = df2.sort_values(by=['FIRMA_ADI', 'FATURA_TARIHI'], ascending=True)

    
        fig = px.line(
            df2,
            x='FATURA_TARIHI',
            y='KAYIT_TARIHI',
            color='FIRMA_ADI',
            markers=True,
            height=700,
            width=1658,
            color_discrete_sequence=px.colors.qualitative.Plotly_r
            )
        
        fig.update_traces(
            text=df2['FIRMA_ADI'],
            textposition='top center',
            mode='lines+markers',
            marker=dict(size=9),
            )

        fig.update_layout(
            plot_bgcolor='midnightblue',
            paper_bgcolor = 'midnightblue',
            title = '', 
            xaxis=dict(title="Tarih", title_standoff=10, showgrid=False, tickfont=dict(color='white'), title_font = dict(color='white')),
            yaxis = dict(title = 'Fatura Kesim Adeti',title_standoff = 10, showgrid = False, zeroline = False, tickfont=dict(color='white'), title_font = dict(color='white')  ),
            showlegend=False,
            margin = dict(l=20, r=70, t=60, b=20),
            autosize = False,
            )
        

        random.seed(30)

        number_of_sirket = df['FIRMA_ADI'].nunique()
        random_array_negatives = np.linspace(-3, -2, int(number_of_sirket / 2))
        random_array_positives = np.linspace(2, 4, int((number_of_sirket + 1) / 2))
        random_array = np.sort(np.concatenate((random_array_negatives, random_array_positives)))
        
        number_of_numbers = len(random_array)
        used_indices = []
    
        last_entries = df2.sort_values(by=['FIRMA_ADI', 'FATURA_TARIHI'], ascending=False).groupby('FIRMA_ADI').head(1)
     
        for sirket_name in firma_selected_input:

            if sirket_name not in df2['FIRMA_ADI'].unique():
                continue
            
            date_values = df2[~(df2['FIRMA_ADI']==i)]['FATURA_TARIHI'].values
            
            sirket_data = df2[df2['FIRMA_ADI'] == sirket_name]
            last_entry = sirket_data.iloc[-1]
            
            remaining_indices = [i for i in range(number_of_numbers) if i not in used_indices]
            random_index = random.choice(remaining_indices)
            used_indices.append(random_index)
            random_number = random_array[random_index]
            
            adjusted_y = last_entry['KAYIT_TARIHI'] + random_number
            y_difference = adjusted_y - last_entry['KAYIT_TARIHI']
            
            last_entry_value_for_i = last_entry['FATURA_TARIHI']
            date_entries_for_i = sirket_data['FATURA_TARIHI'].unique()
            
            if np.count_nonzero(date_values == last_entry_value_for_i) > 1:
                for n in reversed(range(len(sirket_data))):
                    tuple_row = sirket_data.iloc[n]
                    tuple_time = tuple_row['FATURA_TARIHI']
                    if tuple_time not in df2[~(df2['FIRMA_ADI']==sirket_name)]['FATURA_TARIHI'].unique():
                        last_entry = sirket_data.iloc[n]
                        break
             
            fig.add_annotation(
                x=last_entry['FATURA_TARIHI'],
                y=last_entry['KAYIT_TARIHI'],
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                ax=last_entry['FATURA_TARIHI'],
                ay=adjusted_y,
                text=sirket_name,
                showarrow=True,
                arrowhead=4,
                arrowwidth=1.5,
                arrowcolor='cornflowerblue',
                font=dict(size=13, color='cornflowerblue'),
                )
            

            
        st.plotly_chart(fig)

                
                
            
except pyodbc.OperationalError as op_error:
            st.session_state['username_2'] , st.session_state['password_2'] = login_page()
            st.error("Invalid username or password. Please check your username and password.")
            st.write(f'{op_error}')
except pyodbc.DatabaseError as db_error:
            st.session_state['username_2'] , st.session_state['password_2'] = login_page()
            st.error("Error connecting to the database. Please check the server and database details.")
        
except Exception as e:
            st.session_state['username_2'] , st.session_state['password_2'] = login_page()
            st.error(f"An error occurred: {e}")

except ValueError as a:
            st.error(f'Lutfen en az bir sirket secin {a}')
