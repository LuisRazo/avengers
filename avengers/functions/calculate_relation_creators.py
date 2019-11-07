from helpers.helpers import get_data, get_item_from_dynamo, put_item_dynamo

target_avengers = ['ironman', 'capamerica']


def lambda_handler(event, context):
    query = ''' 
SELEC 
    cr.role role,
    array_agg(cr.name) creators
FROM
    target_characters tc
    JOIN characters ct ON tc.character_id = ct.id
    JOIN character_comic cct ON ct.id = cct.character_id
    JOIN creator_comic ccr ON cct.comic_id = ccr.comic_id
    JOIN creators cr ON cr.id = ccr.creator_id
WHERE
    tc.name = {id}
    AND cr.role in ('colorists', 'writers', 'editors')
GROUP BY cr.role
'''
    for aven in target_avengers:
        try:
            item = get_item_from_dynamo(aven, 'creators-avengers-db')
        except:
            item = {}
        partners = get_data(query.format(id=aven))
        put_item_dynamo(item, 'creators-avengers-db')
