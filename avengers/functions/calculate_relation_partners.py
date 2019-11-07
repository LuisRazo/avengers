from helpers.helpers import get_data, get_item_from_dynamo, put_item_dynamo

target_avengers = ['ironman', 'capamerica']


def lambda_handler(event, context):
    query = ''' 
SELEC 
    cr.name character,
    array_agg(co.title) Comics
FROM
    target_characters tc
    JOIN characters ct ON tc.character_id = ct.id
    JOIN character_comic cct ON ct.id = cct.character_id
    JOIN character_comic ccr ON cct.comic_id = ccr.comic_id
    JOIN comics co ON co.id = cct.comic_id
    JOIN characters cr ON cr.id = ccr.character_id
WHERE
    tc.name = {id}
    AND cr.id != ct.id
GROUP BY cr.name
'''
    for aven in target_avengers:
        try:
            item = get_item_from_dynamo(aven, 'partners-avengers-db')
        except:
            item = {}
        partners = get_data(query.format(id=aven))
        put_item_dynamo(item, 'partners-avengers-db')