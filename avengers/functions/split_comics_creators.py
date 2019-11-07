from helpers.helpers import upload_df_S3, read_pickle_from_S3


path = '{file_type}/{date}.p'


def lambda_handler(event, context):
    file_type = event['file_type']
    str_date = event['str_date']
    df = read_pickle_from_S3(path.format(file_type=file_type, date=str_date))     
    print('###SPLIT###')
    df_creators_comics = df[['id', 'creators']]
    df = df[['id', 'title', 'modified']]
    print("###UPLOADING FILE TO S3###")
    upload_df_S3(df, path.format(file_type=file_type, date=str_date))
    upload_df_S3(df_creators_comics, path.format(file_type='creator_comic', date=str_date))

