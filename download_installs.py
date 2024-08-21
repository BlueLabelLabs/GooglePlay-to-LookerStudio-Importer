from google.cloud import storage
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
import os
import datetime
import pandas as pd
import gspread

#These paths in the Docker container need to be mapped to a volume on the host machine
credentials_path = "/app/data/google-credentials.json"
download_folder = "/app/data/installs/"



credentials = service_account.Credentials.from_service_account_file(credentials_path)

start_date = datetime.datetime.strptime(os.getenv('START_DATE'), '%Y-%m-%d')
start_date_time = datetime.datetime.now()
print(f"\INSTALLS UPDATE: Start of execution at  {start_date_time}")

spreadsheet_id = os.getenv('SPREADSHEET_ID')
worksheet_id = os.getenv('INSTALLS_WORKSHEET_NAME')

# Initialize a client
client = storage.Client(credentials=credentials)
bucket_name = os.getenv('PLAY_STORE_BUCKET_NAME')

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # Get the bucket object
    bucket = client.bucket(bucket_name)

    # Get the blob object
    blob = bucket.blob(source_blob_name)

    # Download the blob to a local file
    blob.download_to_filename(destination_file_name)

    print(f"Downloaded storage object {source_blob_name} from bucket {bucket_name} to local file {destination_file_name}.")

#Create a string that is a date in the format of YYYYMM based on today's date
today = datetime.datetime.today()
today = today.strftime('%Y%m')

#Get the days before today to update install data for
days_before_today = int(os.getenv('DAYS_TO_FETCH_INSTALLS_FOR'))
earliest_date_to_fetch = datetime.datetime.today() - datetime.timedelta(days=days_before_today)
#set to midnight of that date
earliest_date_to_fetch = earliest_date_to_fetch.replace(hour=0, minute=0, second=0, microsecond=0)

#Now lets get the installs for the current month
filename = f'installs_com.sunbird.apps_{today}_overview.csv'
destination_filename = f'{download_folder}{filename}'
download_blob(bucket_name, f'stats/installs/{filename}', destination_filename)

#Now we need to convert this csv to a pandas dataframe
df = pd.read_csv(destination_filename, encoding='utf-16')

#We then want to take the dataframe and upload it to a google sheet, overwriting any data for the Date that
#already exists in the Google Sheet
#First we need to authenticate to Google Sheets
credentials = service_account.Credentials.from_service_account_file(credentials_path, 
                                                                    scopes=['https://www.googleapis.com/auth/spreadsheets'])
client = gspread.authorize(credentials)


# Open the Google Sheet
spreadsheet = client.open_by_key(spreadsheet_id)

# Get the worksheet
worksheet = spreadsheet.worksheet(worksheet_id)

# Go through each Date in the Pandas dataframe and update the Google Sheet with the data for that date
for index, row in df.iterrows():
    date = row['Date']
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    date = date_obj.strftime('%m/%d/%Y')

    #If date is before the start date, skip
    if date_obj < start_date:
        print (f"Skipping date {date} as it is before the start date {start_date}")
        continue

    #If date is before the earliest date to fetch, skip
    if date_obj < earliest_date_to_fetch:
        print (f"Skipping date {date} as it is before the earliest date to fetch {earliest_date_to_fetch}")
        continue

    cell = worksheet.find(date, in_column=1)
    if cell:
        cell_row = cell.row
        cell_col = cell.col
        #remove the Date column from the row
        row = row.drop('Date')
        worksheet.update(f'A{cell_row}', [[date]+list(row)])
    else:
        #remove the Date column from the row
        row = row.drop('Date')
        worksheet.append_row([date]+list(row))

end_time = datetime.datetime.now()
duration = end_time - start_date_time
print(f"INSTALLS UPDATE: Finished at {end_time} and took {duration} to execute.")
