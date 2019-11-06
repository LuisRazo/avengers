from helpers.helpers import upload_df_S3, read_pickle_from_S3
from helpers.utils import clean_comic_creator

elements_to_extract = {
        'characters': 
            {
            'function': lambda x: x
            },
        'comic_character': 
            {
            'function': lambda x: x
            },
        'target_characters': 
            {
            'function': lambda x: x
            },
        'comics': 
            {
            'function':lambda x: x
            },
        'creator_comic': 
            {            
            'function':lambda x: clean_comic_creator(x)
            },
        'creators': 
            {
            'function':lambda x: x
            }
    }

path = '{file_type}/{date}.p'


def lambda_handler(event, context):
    file_type = event['file_type']
    str_date = event['str_date']
    elem = elements_to_extract.get(file_type)
    if not elem:
        raise Exception('Unknow file type: ' + file_type)        
    df = read_pickle_from_S3(path.format(file_type=file_type, date=str_date))     
    print('###CLEANSING###')
    df = elem.get('function')(df)
    print("###UPLOADING FILE TO S3###")
    upload_df_S3(df, path.format(file_type=file_type, date=str_date))

