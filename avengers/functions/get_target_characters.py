from helpers.helpers import upload_df_S3, read_pickle_from_S3
import pandas as pd

path = '{file_type}/{date}.p'

def lambda_handler(event, context):
    """Filter out just the target characters"""
    print("###BEGING###")
    file_type = event['file_type']
    str_date = event['str_date']
    if file_type != 'characters':
        raise Exception('Unknow file type: ' + file_type)        
    df = read_pickle_from_S3(path.format(file_type=file_type, date=str_date))     
    print("###GETTING IRONMAN###")
    df_ironman = df[df.name.str.contains('^(iron man)|^tony', case=False)]
    df_ironman['name'] = 'ironman'
    df_ironman = df_ironman[['name', 'id']]
    df_ironman.rename(columns={'id': 'character_id'}, inplace=True)
    print("###GETTING CAP###")
    df_cap = df[df.name.str.contains('^cap.*?ame', case=False)]
    df_cap['name'] = 'ironman'
    df_cap = df_cap[['name', 'id']]
    df_cap.rename(columns={'id': 'character_id'}, inplace=True)
    df_target = pd.concat([df_ironman, df_cap])
    print("###UPLOADING FILE TO S3###")
    upload_df_S3(df_target, path.format(file_type='target_characters', date=str_date))
