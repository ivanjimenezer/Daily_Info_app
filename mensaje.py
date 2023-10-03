import os
from twilio.rest import Client
from twilio_keys import *
import pandas as pd
import requests 
from tqdm import tqdm
from datetime import datetime, timedelta

API_Geo_KEY = GEO_KEY

def getcoordenates(city):
    # Use the API to get coordinates depending on a given City
    # Usamos una API para obtener las coordenadas de una ciudad dada
    url = url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={API_Geo_KEY}'
    response = requests.get(url)
    data = response.json()
    # Check if the query got results
    # Ver si las peticiones tienen resultados
    if data['results']:
        latitude = str(data['results'][0]['geometry']['lat'])
        longitude = str(data['results'][0]['geometry']['lng'])
        #print('Latitude:', latitude)
        #print('Longitude:', longitude)
        coordinates = [latitude, longitude]
        return coordinates
    else:
        print('Coordinates not found for the city.')
        return False
        

def getdate(): 
    dates = []
    # We obtain the current date
    # Obtenemos la fecha actual y la del dia siguiente 
    current_date = datetime.now().date()
    #print(current_date)
    # Add one day
    one_day = timedelta(days=1)
    next_day = current_date + one_day
    #print(next_day)
    dates =[current_date.strftime("%Y-%m-%d"), next_day.strftime("%Y-%m-%d")]
    return dates
    
# DAILY DATA TO BE SEND / DATOS DIARIOS QUE SERAN ENVIADOS

#----Weather conditions / Condiciones del clima
def get_weatherdata(coordinates, dates):
    url_clima = 'https://api.open-meteo.com/v1/forecast?latitude='+coordinates[0]+'&longitude='+coordinates[1]+'&hourly=temperature_2m,precipitation_probability,cloudcover&daily=temperature_2m_max,temperature_2m_min&timezone=auto&start_date='+dates[0]+'&end_date='+dates[1]
    response = requests.get(url_clima).json()
    #print(response.keys())
    return response

#--------Hourly Variables
#--------temperature
def gethdata(response):
    # Getting the data out from the response
    # Getting the temperature
    h_temstr = response['hourly']['temperature_2m']
    h_tem = [int(num) for num in h_temstr]
    #--------Precipitation probability
    h_preci = response['hourly']['precipitation_probability']
    #--------Percentage of sky covered in clouds
    h_cloud = response['hourly']['cloudcover']
    #-----SEPARATE DATE AND TIME
    timestamp = response['hourly']['time']
    h_time = []
    h_date = []
    # Getting the hours and days
    for x in timestamp:
        date,time = x.split('T')
        h_time.append(time)
        h_date.append(date)
    #---- Creating the Dataframe for the hourly variables
    columns = ['Date','Hour', 'Temperature 2m', 'Precipitation Probability', 'Cloud Covering']
    hourly_data = list(zip(h_date,h_time, h_tem, h_preci, h_cloud))
    df = pd.DataFrame(hourly_data, columns=columns)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


#--------Daily Variables
def getddata(response, h_df):
    #-------- Time anda Date 
    d_date = response['daily']['time']
    d_date
    #-------- Maiximum Temperature of the day
    d_temp_max = response['daily']['temperature_2m_max']
    #print(d_temp_max)    
    #--------Minimal Temperature
    d_temp_min = response['daily']['temperature_2m_min']
    #print(d_temp_min) 
    
    #---- Creating the Dataframe for the daily variables
    #------ Creating the mean temperature of the day
    #  getting the temperature and the day
    df_date = h_df[['Date','Temperature 2m']]
    # groping the data so we can get the mean
    mean_temperatures = df_date.groupby('Date')['Temperature 2m'].mean()
    d_mean_temp = mean_temperatures.round(2).tolist()
    # The dataframe
    daily_columns = ['Date','Mean Temperature', 'Max Temperature 2m', 'Min Temperature 2m']
    daily_data = list(zip(d_date, d_mean_temp, d_temp_max, d_temp_min))
    d_df = pd.DataFrame(daily_data, columns=daily_columns)
    #print(h_df.head())
    return d_df

#Formating the probabilities as percentages %
def percent(dafr):
    columns = ['Precipitation Probability', 'Cloud Covering']
    for col in columns:
        dafr[col] = dafr[col].apply(lambda x: f'{x}%')
        
def datapreparation(d_df, h_df):
    
    #----Changing the numered dates for "Today" and "Tomorrow"
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    h_df['Day'] =  h_df['Date'].apply(lambda x: 'Today' if x.date() == today else ('Tomorrow' if x.date() == tomorrow else x.strftime('%Y-%m-%d')))
    # High probability of rain
    hdf_preci = h_df[(h_df['Precipitation Probability']>85) ]
    # Changing into Percentages
    percent(hdf_preci)
    hdf_preci = hdf_preci[['Day','Hour','Precipitation Probability','Cloud Covering']]

    #--------Shorting the columns names
    hdf_preci.rename(columns={'Precipitation Probability': 'Precipitation', 'Cloud Covering':'Cloud Covering'}, inplace=True)
    
    #--------In which moments it will be cloudy?
    hdf_cloudy = h_df[ (h_df['Cloud Covering']>85)]
    
    #--------In which moments it will be sunny?
    hdf_notcloudy = h_df[ (h_df['Cloud Covering']<10)]
    return hdf_preci
def send_message(message):
    # SEND THE PHONE MESSAGE
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                    to=MY_PHONE_NUMBER,
                    from_=PHONE_NUMBER,
                    body=message
                )
    print('Mensaje Enviado: '+message.sid)

def main():
    #Get city
    CITY = input("Please enter the City where you're located': ")
    # Get coordenates
    coor_response = getcoordenates(CITY)
    # If we didnt get nothing then it does nothing
    if(coor_response == False):
        return
    # Get Dates
    dates = getdate()
    # Get weather forecasting data
    weather_response = get_weatherdata(coor_response, dates)
    # get hourly data
    h_df = gethdata(weather_response)
    # get daily data
    d_df = getddata(weather_response, h_df)
    # Prepare and clean the data
    df_final = datapreparation(d_df, h_df)
    
    # turn the dataframe into a string
    df_message = df_final.to_string(index=False)
    
    message = "\n Good Morning. \n The weather forecast for today (" + dates[0] + ") and tomorrow (" + dates[1] + ") in " + CITY + " is \n" + df_message
    print(message)
    send_message(message)

if __name__ == "__main__":
    main()













