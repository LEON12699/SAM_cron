import json
import requests
import os
from pathlib import Path
import boto3
import datetime
import sops

API_URL = "https://pro-api.coinmarketcap.com/v1"
ENDPOINT = "/cryptocurrency/listings/latest"
LIMIT = 5000  # MAX LIMIT API CAN EXECUTE


def get_sops_secrets(path):
    pathtype = sops.detect_filetype(path)
    tree = sops.load_file_into_tree(path, pathtype)
    sops_key, tree = sops.get_key(tree)
    return sops.walk_and_decrypt(tree, sops_key)



def lambda_handler(event, context):

    API_KEY = get_sops_secrets('secret.json').get('API_TOKEN')


    S3_BUCKET = os.getenv('S3_BUCKET', 'appCrypto')
    S3_STORAGE_PATH = os.getenv('S3_STORAGE_PATH', 'documents/')
    S3_OBJECT_PREFIX =os.getenv('S3_OBJECT_PREFIX', 'cryto_prices_')
    S3_OBJECT_SUFFIX= os.getenv('S3_OBJECT_SUFFIX', '.json')
    
    URL = f'{API_URL}{ENDPOINT}?limit={LIMIT}'
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY
    }
    
    
    data_formatted= []
    print("searching prices...")
    try:
        response = requests.request("GET", URL, headers=headers)
        crypto_data = response.json();

        data_formatted += [
            {
                'name': crypto.get('name'),
                'symbol': crypto.get('symbol'),
                'price': crypto.get('quote').get('USD').get('price'),
                "volume_24h": crypto.get('quote').get('USD').get('volume_24h'),
                "volume_change_24h": crypto.get('quote').get('USD').get('volume_change_24h'),
                "percent_change_24h":crypto.get('quote').get('USD').get('percent_change_24h'),
                "percent_change_7d":crypto.get('quote').get('USD').get('percent_change_7d') ,
                
            }
            for crypto in crypto_data.get('data', [])
        ]
        print("End search .. :)")
        
    except requests.exceptions.RequestException as e: 
        print("something has gone wrong")
        raise SystemExit(e)

    file_name = S3_STORAGE_PATH + S3_OBJECT_PREFIX \
        + datetime.datetime.utcnow().strftime('%Y-%m%d-%H%M-%S') \
        + S3_OBJECT_SUFFIX

    print(f'Uploading {file_name} to {S3_BUCKET} ...')
    
    print(f'{data_formatted=}')
    
    s3 = boto3.resource('s3')
    s3.Object(
        S3_BUCKET,
        file_name
    ).put(Body=json.dumps(data_formatted))

    print('Upload successful.')

    return {
        "statusCode": 200,
        "S3_PATH": f's3://{S3_BUCKET}/{file_name}'
    }

