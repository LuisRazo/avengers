import requests
from src.utils.extractors import paginator

def lambda_handler(event, context):
    url = "https://gateway.marvel.com:443/v1/public/characters"

    querystring = {"orderBy":"-modified","apikey":"87a1c6ea5695c46726e54f9cf71322e3"}

    headers = {
    'Accept': "application/json",
    'Origin': "https://test.albo.mx",
    'Referer': "https://developer.marvel.com/docs"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

