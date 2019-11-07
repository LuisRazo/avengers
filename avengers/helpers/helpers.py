# coding=utf-8


class AVException(Exception):
    pass


def get_item_from_dynamo(id):
    """
    Get item from DynamoDB
    :param uuid: Identifier for the item
    :return: dict item retrieved from DynamoDB
    """
    from os import environ
    from boto3 import resource

    av_dynamo = environ["AV_DYNAMO"]
    table = resource('dynamodb', region_name='us-west-2').Table(av_dynamo)
    try:
        response = table.get_item(Key={'id': id})
    except:
        raise AVException('Something went bad while retrieving the item')
    item = response.get('Item')
    if not item:
        raise AVException('The item does not exist')
    return item


def put_item_dynamo(item):
    """
    Put item into DynamoDB
    :param item: dict to insert in dynamodb
    """
    from os import environ
    from boto3 import resource

    av_dynamo = environ["AV_DYNAMO"]
    table = resource('dynamodb', region_name='us-west-2').Table(av_dynamo)
    table.put_item(Item=item)


def download_file_from_S3(file_name):
    """
    Download file from specified S3 path.
    :param file_name: Path to file in S3
    :return: file in bytes
    """
    from os import environ
    from boto3 import resource

    bucket_files = environ["BUCKET_FILES"]

    s3 = resource('s3')
    try:
        file_ = s3.Object(bucket_files, file_name).get()['Body']
    except:
        raise
    return file_


def upload_df_S3(df, path):
    """
    Upload dataframe to S3
    :param df: dataframe to upload
    :param path: Path to save dataframe
    """
    from os import environ
    from io import BytesIO
    from boto3 import resource

    bucket_files = environ["BUCKET_FILES"]
    pickle_buffer = BytesIO()
    s3_resource = resource('s3')
    df.to_pickle(pickle_buffer, compression=None)
    s3_resource.Object(bucket_files, path).put(Body=pickle_buffer.getvalue())


def read_pickle_from_S3(key):
    """
    Read pickle from S3
    :param key: path of the file in S3
    :return df:
    """
    from pandas import read_pickle
    from os import environ
    from io import BytesIO
    from boto3 import client

    s3 = client('s3')
    bucket_files = environ["BUCKET_FILES"]
    obj = s3.get_object(Bucket=bucket_files, Key=key)
    df = read_pickle(BytesIO(obj['Body'].read()), compression=None)
    return df


def get_data(query):
    from sqlalchemy import create_engine
    from os import environ
    from pandas import read_sql
    eng_str = ('postgresql://{user}:{passw}@{host}:{port}/{dbname}'
               ).format(user=environ['RDS_USERNAME'],
                        passw=environ['RDS_PASSWORD'],
                        host=environ['RDS_HOSTNAME'],
                        port=environ['RDS_PORT'],
                        dbname=environ['RDS_DBNAME'])

    engine = create_engine(eng_str)
    df = None
    conn = engine.connect()
    try:
        # select information from db
        df = read_sql(sql=query, con=conn)
    except:
        raise
    finally:
        conn.close()
    return df


def upsert_query(cols, target_table, tmp_table, pkeys):
    query = 'INSERT INTO {} '.format(target_table)
    query += '({}) '.format(', '.join(['"{}"'.format(col) for col in cols]))
    query += 'SELECT '
    query += ', '.join(['{0}."{1}"'.format(tmp_table, col) for col in cols])
    query += ' FROM {} '.format(tmp_table)
    query += 'ON CONFLICT '
    query += '({}) '.format(', '.join(['"{}"'.format(col) for col in pkeys]))
    query += 'DO UPDATE SET '
    query += ', '.join(['{0} = EXCLUDED.{0}'.format(col) for col in set(cols) - set(pkeys)])
    return query


def upsert_df_to_postgres(df, table_name, tmp_table, pkeys, dtype=None):
    from sqlalchemy import create_engine
    from os import environ
    eng_str = ('postgresql://{user}:{passw}@{host}:{port}/{dbname}'
               ).format(user=environ['RDS_USERNAME'],
                        passw=environ['RDS_PASSWORD'],
                        host=environ['RDS_HOSTNAME'],
                        port=environ['RDS_PORT'],
                        dbname=environ['RDS_DBNAME'])

    engine = create_engine(eng_str)
    # insert to tmp table
    df.to_sql(tmp_table, engine, if_exists='replace', dtype=dtype)
    # insert to destiny table
    conn = engine.connect()
    try:
        conn.execute(upsert_query(cols=df.columns,
                                  target_table=table_name,
                                  tmp_table=tmp_table,
                                  pkeys=pkeys))
        conn.execute('DROP TABLE {}'.format(tmp_table))
    except:
        raise
    finally:
        conn.close()

