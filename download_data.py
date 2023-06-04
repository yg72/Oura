import requests
import datetime
import pandas as pd
from sqlalchemy import create_engine # read from sql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

#load toke file

eng = create_engine('mysql+pymysql://c391tujwolvmij5a:tqkzvprrc96kcm2g@frwahxxknm9kwy6c.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/rjb11pca4j89kh0x')
token_df=pd.read_sql("tokens",con=eng,index_col='id')
token_list = list(token_df['oauth_token'])
print(token_df)

import requests
import datetime
import pandas as pd
from sqlalchemy import create_engine # read from sql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

#load toke file

eng = create_engine('mysql+pymysql://c391tujwolvmij5a:tqkzvprrc96kcm2g@frwahxxknm9kwy6c.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/rjb11pca4j89kh0x')
token_df=pd.read_sql("tokens",con=eng,index_col='id')
token_list = list(token_df['oauth_token'])
print(token_df)
# IDS  = [] #List of participant IDs to download data

for i in range(token_df.shape[0]):
    
    # Set access token, client secret, and client ID
    access_token = token_list[i]
    print(access_token)
    client_secret = ""
    client_id = ""

    # Set date range for data retrieval
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    start_date = yesterday.strftime("%Y-%m-%d")
    end_date = yesterday.strftime("%Y-%m-%d")
    
    id_path = str(i)+'_'+start_date

    # Set API endpoint URLs
    base_url = "https://api.ouraring.com/v1"
    #resolution = 1 to download minute by minute data
    activity_url = f"{base_url}/activity?start={start_date}&end={end_date}&resolution=1"
    sleep_url = f"{base_url}/sleep?start={start_date}&end={end_date}&resolution=1"
    hr_url = f"{base_url}/readiness?start={start_date}&end={end_date}&resolution=1"
    summary_url = f"{base_url}/sleep?summary=tue&start={start_date}&end={end_date}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Get activity data
    activity_data = requests.get(activity_url, headers=headers).json()
    # Get sleep data
    sleep_data = requests.get(sleep_url, headers=headers).json()
    # Get heart rate data
    hr_data = requests.get(hr_url, headers=headers).json()
    # Get daily summary data
    summary_data = requests.get(summary_url, headers=headers).json()

    print(activity_data)