from helpers.helpers import upload_df_S3, read_pickle_from_S3
from helpers.utils import paginator
import pandas as pd
import os

elements_to_extract = {        
        'comic_character': 
            {'end_point': 'characters/{character_id}/comics',
            'values': ['id']
            }        
    }

path = '{file_type}/{date}.p'

def lambda_handler(event, context):
    apikey = os.environ['APIKEY']
    print('###BEGIN###')
    file_type = event['file_type']
    str_date = event['str_date']
    if file_type != 'characters':
        raise Exception('Unknow file type: ' + file_type)        
    
    df = read_pickle_from_S3(path.format(file_type=file_type, date=str_date))     

    url = "https://gateway.marvel.com:443/v1/public/{end_point}"
    headers = {
    'Accept': "application/json",
    'Origin': "https://test.albo.mx",
    'Referer': "https://developer.marvel.com/docs"
    }        
    elem = elements_to_extract.get('comic_character')    
    end_point = elem.get('end_point')
    url = url.format(end_point=end_point)
    comics_character = []
    for character_id in df.id:
        querystring = {
        "apikey":"87a1c6ea5695c46726e54f9cf71322e3",
        "limit":100,
        "offset": 0,
        "orderBy": "-modified"
        }        
        
        print('working on: ' + str(character_id))
        results = paginator(url.format(character_id=character_id), querystring, headers)
        data = [{
            x: res[x]
            for x in elem['values']
            } for res in results]
    
        df = pd.DataFrame(data)        
        df.rename(columns={'id': 'comic_id'}, inplace=True)
        if not df.empty:
            df['character_id'] = character_id
            comics_character.append(df)
    
    df_comic_char = pd.concat(comics_character)    
    upload_df_S3(df_comic_char, path.format(file_type='comic_character', date=str_date))
