import json

def lambda_handler(event, context):
    # TODO implement    
    print(event.get('pathParameters').get('id'))
    print(event)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
