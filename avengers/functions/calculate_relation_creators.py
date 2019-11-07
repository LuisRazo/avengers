from helpers.helpers import get_data, get_item_from_dynamo, put_item_dynamo
import datetime

target_avengers = ['ironman', 'capamerica']


def lambda_handler(event, context):
    query = ''' 
SELECT
    ccr.role,
    array_agg(DISTINCT cr.full_name) creators
FROM
    target_characters tc
    JOIN characters ct ON tc.character_id = ct.id
    JOIN character_comic cct ON ct.id = cct.character_id
    JOIN creator_comic ccr ON cct.comic_id = ccr.comic_id
    JOIN creators cr ON cr.id = ccr.creator_id
WHERE
    tc.name = '{id}'
    AND ccr.role in ('colorist', 'writer', 'editor')
GROUP BY ccr.role;
'''

    for aven in target_avengers:        
        df = get_data(query.format(id=aven))
        creators = {}
        for index, row in df.iterrows():
            creators[row.role] = row.creators
        str_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        creators.update({'last_sync': str_now})
        put_item_dynamo({'id': aven, 'response': creators}, 'creators-avengers-db')
