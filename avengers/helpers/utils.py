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
    return comic_creator


def clean_comic_creator(df_creators_comics):    
    comics_creators = []
    for index, row in df_creators_comics.iterrows():
        comic_id = row['id']
        comics_creators += [get_comic_creator(comic_id, item) for item in  row['creators']['items']]
    df_creators_comics = pd.DataFrame(comics_creators)
    return df_creators_comics