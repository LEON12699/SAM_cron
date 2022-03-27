#! /bin/bash

set -e 

echo "MAKE THE CALL"
curl 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?sort_dir=desc&limit=5000'  --request GET --header "X-CMC_PRO_API_KEY:$MY_API_KEY" | jq .> test.json 
# TODO TRY TO  BY PRICE USD