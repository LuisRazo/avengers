# coding=utf-8
from helpers.helpers import read_pickle_from_S3, upsert_df_to_postgres


elements_to_db = { 
    'characters': {'db': {'table_name': 'characters', 'tmp_table': 'characters_tmp', 'pkeys': ['id']}},            
    'character_comic': {'db': {'table_name': 'character_comic', 'tmp_table': 'character_comic_tmp', 'pkeys': ['comic_id', 'character_id']}},            
    'target_characters': {'db': {'table_name': 'target_characters', 'tmp_table': 'target_characters_tmp', 'pkeys': ['name']}},            
    'comics': {'db': {'table_name': 'comics', 'tmp_table': 'comics_tmp', 'pkeys': ['id']}},            
    'creator_comic': {'db': {'table_name': 'creator_comic', 'tmp_table': 'creator_comic_tmp', 'pkeys': ['comic_id', 'creator_id']}},            
    'creators': {'db': {'table_name':'creators', 'tmp_table': 'creators_tmp', 'pkeys': ['id']}}
    }

path = '{file_type}/{date}.p'

def lambda_handler(event, context):    
    file_type = event['file_type']
    str_date = event['str_date']
    path = path.format(file_type=file_type, date=str_date)
    elem_db = elements_to_db.get(file_type)
    if not elem_db:
        raise Exception('Unknow file type: ' + file_type)
    table_name = elem_db.get('db').get('table_name')
    tmp_table = elem_db.get('db').get('tmp_table')
    pkeys = elem_db.get('db').get('pkeys')
    print("######GETTING PICKLE######")    
    file_ = read_pickle_from_S3(path.format(file_type=file_type, date=str_date))     
    print("######UPSERTING DATA######")
    upsert_df_to_postgres(df=file_, table_name=table_name,
                          tmp_table=tmp_table,
                          pkeys=pkeys
                          )
    print("######SUCCESS######")
    return event
