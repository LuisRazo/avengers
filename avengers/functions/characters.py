import json
from helpers.helpers import get_item_from_dynamo

target_avengers = ['ironman', 'capamerica']

def lambda_handler(event, context):    
    aven = event.get('pathParameters').get('id')
    if not aven in target_avengers:
        return {
        'statusCode': 400,
        'body': json.dumps('id invalido')
    }
    item = get_item_from_dynamo(aven, 'partners-avengers-db')    
    return {
        'statusCode': 200,
        'body': json.dumps(item['response'])
    }
