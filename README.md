# Daily_Info_app
I always wanted to stay ahead of the events and preventing problems. Because of that I developed a daily notifier to keep me informed about weather forecasting and planning my city routes, clothing and activities by sending me telephone messages.
In this application using different sources of information, I receive information about specific subjects every day to aid in my planning and decision-making.
I used [Twilio](https://www.twilio.com) for the backend services, APIS ([OpenCage Geocoding](https://api.opencagedata.com/), [Open-meteo](https://open-meteo.com/en/docs)) for retrieving data and Pandas for data cleaning.
This is the expected output of the app. It will tell me the:
* Day (Today and Tomorrow)
* Time (24hr format)
* Precipitation Probability (%) 
* Cloud Covering (%)

<img src="https://github.com/ivanjimenezer/Daily_Info_app/blob/main/output3.jpg" alt="Image Alt Text" width="480" height="960">
The app can accept different cities, depending on correct spelling.

## Ciudad de Mexico
<img src="https://github.com/ivanjimenezer/Daily_Info_app/blob/main/output1.jpg" alt="Image Alt Text" width="480" height="480">

## XALAPA
<img src="https://github.com/ivanjimenezer/Daily_Info_app/blob/main/output2.jpg" alt="Image Alt Text" width="420" height="480">

Now the next step is implementing it in AWS. That will be in Daily_Info_app.v2
