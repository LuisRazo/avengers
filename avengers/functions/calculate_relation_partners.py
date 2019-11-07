from helpers.helpers import get_data, get_item_from_dynamo, put_item_dynamo
import datetime

target_avengers = ['ironman', 'capamerica']


def lambda_handler(event, context):
    query = ''' 
SELECT 
    cr.name as character,
    array_agg(co.title) as Comics
FROM
    target_characters tc
    JOIN characters ct ON tc.character_id = ct.id
    JOIN character_comic cct ON ct.id = cct.character_id
    JOIN character_comic ccr ON cct.comic_id = ccr.comic_id
    JOIN comics co ON co.id = cct.comic_id
    JOIN characters cr ON cr.id = ccr.character_id
WHERE
    tc.name = '{id}'
    AND cr.id != ct.id
GROUP BY cr.name
'''
    for aven in target_avengers:        
        partners = get_data(query.format(id=aven))
        char_com = df.to_dict(orient='records')
        str_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        response = {'last_sync': str_now,
                    'characters': char_com}
        put_item_dynamo({'id': aven, 'response': response}, 'partners-avengers-db')