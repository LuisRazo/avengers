from helpers.utils import paginator
from helpers.helpers import upload_df_S3
from datetime import datetime
import pandas as pd
import os


elements_to_extract = {
        'characters': 
            {'end_point': 'characters',
            'values': ['id', 'name', 'modified']
            },
        'comic_character': 
            {'end_point': 'characters/{character_id}/comics',
            'values': ['id']
            },
        'target_characters': 
            {'end_point': 'characters',
            'values': ['id', 'name', 'modified']
            },
        'comics': 
            {'end_point': 'comics',
            'values':['id', 'title', 'creators', 'modified']
            },
        'creator_comic': 
            {
            'end_point': 'comics',
            'values':['id', 'title', 'creators', 'modified']
            },
        'creators': 
            {'end_point': 'creators',
            'values':['id', 'fullName', 'modified']
            }
    }

path = '{file_type}/{date}.p'

def lambda_handler(event, context):
    """Get data from avengers api and save it in s3"""
    apikey = os.environ['APIKEY']
    print('###BEGIN###')
    file_type = event['file_type']
    str_time = event['time']        
    print("###PARSING DATES###")
    dt_date = datetime.strptime(str_time, '%Y-%m-%dT%H:%M:%SZ')
    str_date = dt_date.strftime("%Y-%m-%d")

    url = "https://gateway.marvel.com:443/v1/public/{end_point}"
    headers = {
    'Accept': "application/json",
    'Origin': "https://test.albo.mx",
    'Referer': "https://developer.marvel.com/docs"
    }    
    querystring = {
        "apikey": apikey,
        "limit":100,
        "offset": 0,
        "orderBy": "-modified",
        "modifiedSince": str_date
        }
    
    elem = elements_to_extract.get(file_type)
    if not elem:
        raise Exception('Unknow file type: ' + file_type)
    end_point = elem.get('end_point')
    print("###BEGINIG PAGINATOR###")
    results = paginator(url.format(end_point=end_point), querystring, headers)
    data = [{
            x: res[x]
            for x in elem['values']
            } for res in results]
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='id', inplace=True)     
    #we need to control the modified date ourself because we can't trust in the modified date from api avengers
    df['modified'] = dt_date        
    print("###UPLOADING FILE TO S3###")
    upload_df_S3(df, path.format(file_type=file_type, date=str_date))

