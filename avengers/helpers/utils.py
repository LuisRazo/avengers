import requests
import time
import pandas as pd


def paginator(url, params, headers):
    count = -1
    results = []
    offset = params.get('offset')
    while count != 0:
        response = requests.request("GET", url, headers=headers, params=params)        
        res_json = response.json()
        print(res_json)
        results += res_json.get('data').get('results')
        count = res_json.get('data').get('count')
        print('pagination on:' + str(offset))
        offset = offset + 100
        params['offset'] = offset
        time.sleep(1)
    return results


def general_clean(df):
    df['modified'] = pd.to_datetime(df.modified, utc=True, errors='coerce')
    return df


def get_comic_creator(comic_id, item):
    creator_id = item.get('resourceURI').split('/')[-1]
    comic_creator = {'comic_id': comic_id,
                     'role': item.get('role'),
                     'creator_id': creator_id}


