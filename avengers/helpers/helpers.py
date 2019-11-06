# coding=utf-8


class IMException(Exception):
    pass


def get_item_from_dynamo(uuid):
    """
    Get item from DynamoDB
    :param uuid: Identifier for the item
    :return: dict item retrieved from DynamoDB
    """
    from os import environ
    from boto3 import resource

    otr_dynamo = environ["OTR_DYNAMO"]
    table = resource('dynamodb', region_name='us-west-2').Table(otr_dynamo)
    try:
        response = table.get_item(Key={'uuid': uuid})
    except:
        raise IMException('Algo salió mal al obtener el item')
    item = response.get('Item')
    if not item:
        raise IMException('No existe el item')
    return item


def put_item_dynamo(item):
    """
    Put item into DynamoDB
    :param item: dict to insert in dynamodb
    """
    from os import environ
    from boto3 import resource

    otr_dynamo = environ["OTR_DYNAMO"]
    table = resource('dynamodb', region_name='us-west-2').Table(otr_dynamo)
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


def read_input_file(file_name):
    """
    Read SAP from specified bytes file or path.
    :param file_name: Path to input file in SAP- or bytes_file
    :return: Pandas DataFrame with SAP data.
    """
    from pandas import read_csv
    # Read SAP file
    sap = read_csv(file_name, sep='\t',
                   encoding='utf-16',
                   skiprows=[0, 1, 2, 3, 4],
                   skip_blank_lines=True,
                   dtype=object)
    # Remove spaces in column names
    sap.columns = [x.strip() for x in sap.columns.tolist()]
    return sap


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
    df.to_pickle(pickle_buffer)
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
    df = read_pickle(BytesIO(obj['Body'].read()))
    return df


def rename_file_s3(key, new_key):
    """
    Read pickle from S3
    :param key: path of the file in S3
    :return df:
    """
    from os import environ
    from io import BytesIO
    from boto3 import resource

    s3_resource = resource('s3')
    bucket_files = environ["BUCKET_FILES"]
    s3_resource.Object(bucket_files, new_key).copy_from(CopySource=bucket_files + '/' + key)
    s3_resource.Object(bucket_files, key).delete()


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
    # insert to destiny table
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


def send_message_slack(message):
    from slackclient import SlackClient
    from os import environ

    slack_token = environ["SLACK_API_TOKEN"]
    slack_channel = environ["SLACK_CHANNEL"]
    slack_username = environ["SLACK_USERNAME"]

    sc = SlackClient(slack_token)
    sc.api_call("chat.postMessage", username=slack_username, channel=slack_channel,
                text=message)


def delete_sqs_message(receipt_handle):
    from boto3 import client
    from os import environ

    sqs = client('sqs')
    url_queue = environ['URL_SQS']

    return sqs.delete_message(
        QueueUrl=url_queue,
        ReceiptHandle=receipt_handle
    )
