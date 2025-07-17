import dlt 
import duckdb
import pandas as pd
import requests
from io import StringIO, BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

#set credential
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

creds = service_account.Credentials.from_service_account_file(
    r"BelajarDLT/service_account.json",  # Replace with your actual key path
    scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=creds)
sheets_service = build("sheets", "v4", credentials=creds)

def download_file_from_drive(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

#set pipeline
pipeline = dlt.pipeline(
    pipeline_name = "data_pipeline",
    destination = "duckdb",
    dataset_name = "booking_data"
)

#file .csv yang disimpan dalam google drive
#download file
@dlt.resource(table_name='df_data_csv')
def get_csv():
    file_id = "1T0pgh2bBmSUAZwNe_BnpHueg-_pxfEE7"
    file_obj = download_file_from_drive(file_id)
    # decode byte stream to string
    csv_data = StringIO(file_obj.read().decode('utf-8'))
    df = pd.read_csv(csv_data)
    yield df

#file .xls yang disimpan dalam google drive
@dlt.resource(table_name='df_data_xls')
def get_xls():
    file_id = "1ZNIR59Rc4zSBWjrRG9jFtrJN1HMHZ6ip"
    file_obj = download_file_from_drive(file_id)
    df = pd.read_excel(file_obj)
    yield df

#file google sheet
@dlt.resource(table_name='df_data_sheet')
def get_google_sheet():
    spreadsheet_id = "1bqT5ubxnxZTnq-Kae-pFuKhY9C4iDA9LsN24uhiqw54"
    range_name = "Sheet1"  # change this to match your actual sheet/tab name

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])
    if not values:
        print("No data found.")
        return

    # Assume first row is header
    df = pd.DataFrame(values[1:], columns=values[0])
    yield df

@dlt.source
def all_data():
    return get_csv, get_xls, get_google_sheet

load_info = pipeline.run(all_data())
print(load_info)