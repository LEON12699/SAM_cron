import json
import requests
import os
from pathlib import Path

# You can reference EFS files by including your local mount path, and then
# treat them like any other file. Local invokes may not work with this, however,
# as the file/folders may not be present in the container.
API_URL = "https://pro-api.coinmarketcap.com/v1"
ENDPOINT = "/cryptocurrency/listings/latest"
LIMIT = 5000  # MAX LIMIT API CAN EXECUTE
API_KEY = os.getenv("MY_API_KEY")
#FILE = Path("/mnt/lambda/file")


def lambda_handler(event, context):
    URL = f'{API_URL}{ENDPOINT}?limit={LIMIT}'
    
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY
    }
    

    print("searching prices...")
    try:
        response = requests.request("GET", URL, headers=headers)
        data = response.json();
        print("End search .. :)")
        #print(data['data'])
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("something has gone wrong")
        raise SystemExit(e)
    wrote_file = False
    contents = None
    
    print(data['data'])
    # The files in EFS are not only persistent across executions, but if multiple
    # Lambda functions are mounted to the same EFS file system, you can read and
    # write files from either function.
    if not FILE.is_file():
        with open(FILE, 'w') as f:
            contents = "Hello, EFS!\n"
            f.write(contents)
            wrote_file = True
    else:
        with open(FILE, 'r') as f:
            contents = f.read()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "file_contents": contents,
            "created_file": wrote_file
        }),
    }


lambda_handler({},{})