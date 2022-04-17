import os.path

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import boto3
import json
from datetime import datetime

# If modifying these scopes, delete the file token.json.
# TODO put variables on template yaml
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1HP9rwQKJiTERiB18us0cJUinfpp9Yvuh_7A_FFJvxIE'

def getRangeName(sheet_name: str):
    return f"'{sheet_name}'!A:H"


def lambda_handler(event, context):
    
    print("context", context)
    HEADERS = ['NAME', 'SYMBOL', 'PRICE', 'VOLUME 24H',
               'VOLUME CHANGE 24H', 'PERCENT CHANGE 24H', 'PERCENT CHANGE 7D']
    S3_OBJECT = event['Records'][0].get('s3')
    S3_BUCKET = S3_OBJECT.get('bucket').get('name')
    S3_URL_OBJECT = S3_OBJECT.get('object').get('key')

    s3 = boto3.resource('s3')
    obj = s3.Object(S3_BUCKET, S3_URL_OBJECT)
    DATA_S3 = obj.get()['Body'].read()
    Data = json.loads(DATA_S3)

    NAME_SHEET = datetime.now().strftime("%B %d, %Y / %I:%M:%S%p")

    print('Pulling a list of what data already exists in the target Google Sheet...')

    # TODO encrypt credentials with sop
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', SCOPES)

    sheets_service = build('sheets', 'v4', credentials=creds)

    requests = []
    # Create a new sheet 
    requests.append({
        "addSheet": {
            "properties": {
                "title": f'{NAME_SHEET}',
                "sheetType": 'GRID',
                "gridProperties": {
                    "rowCount": len(Data) + 1,
                    "columnCount": len(HEADERS),
                },
                "tabColor": {
                    "green": 0.3,
                }
            }
        }
    })

    body = {
        'requests': requests
    }

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    # pk_count = len(extracted_sheet_data_pks) + 2 # adding an additional row for the header and for an offset of 1 for inserting

    RANGE_UPDATE = getRangeName(NAME_SHEET)
    data = [[
        row.get('name'),
        row.get('symbol'),
        row.get('price'),
        row.get('volume_24h'),
        row.get('volume_change_24h'),
        row.get('percent_change_24h'),
        row.get('percent_change_7d')
    ] for row in Data]

    data.insert(0, HEADERS)

    # TODO improve styles of sheet
    
    body = {
    'values': data
    }
    
    result = sheets_service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID, range=RANGE_UPDATE,
    valueInputOption="RAW", body=body).execute()
    
    
    s3.Object(S3_BUCKET, S3_URL_OBJECT).delete()

    return {
        "statusCode": 200,
        "result": result
    }
