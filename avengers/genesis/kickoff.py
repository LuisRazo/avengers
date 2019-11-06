import pandas as pd
from avengers.utils import paginator, general_clean, get_comic_creator


elements_to_extract = {
        'characters': 
            {'end_point': 'characters',
            'values': ['id', 'name', 'modified'],
            'function': lambda x:x
            },
        'comic_character': 
            {'end_point': 'characters/{character_id}/comics',
            'values': ['id'],
            'function': lambda x:x
            },
        'target_characters': 
            {'end_point': 'characters',
            'values': ['id', 'name', 'modified'],
            'function': lambda x:x
            },
        'comics': 
            {'end_point': 'comics',
            'values':['id', 'title', 'creators', 'modified'],
            'function': lambda x:x
            },
        'creator_comic': 
            {
            'end_point': 'comics',
            'values':['id', 'title', 'creators', 'modified'],
            'function': lambda x:x
            },
        'creators': 
            {'end_point': 'creators',
            'values':['id', 'fullName', 'modified'],
            'function': lambda x:x
            }
    }


def main():        
    url1 = "https://gateway.marvel.com:443/v1/public/{end_point}"
    headers = {
    'Accept': "application/json",
    'Origin': "https://test.albo.mx",
    'Referer': "https://developer.marvel.com/docs"
    }
    print(url1)
    querystring = {
            "apikey":"87a1c6ea5695c46726e54f9cf71322e3",
            "limit":100,
            "offset": 0,
            "orderBy": "-modified"
            }
    elem = elements_to_extract.get('creators')
    end_point = elem.get('end_point')
    print('working on ' + end_point)
    results = paginator(url1.format(end_point=end_point), querystring, headers)
    data = [{
            x: res[x]
            for x in elem['values']
            } for res in results]
    print(len(data))
    df = pd.DataFrame(data)
    df = general_clean(df)
    df = elem.get('function')(df)        
    df.drop_duplicates(subset='id', inplace=True) 
    upsert_df_to_postgres(df=df, **elem.get('db'))
    

    querystring = {
            "apikey":"87a1c6ea5695c46726e54f9cf71322e3",
            "limit":100,
            "offset": 0,
            "orderBy": "-modified"
            }
    elem = elements_to_extract.get('comics')
    end_point = elem.get('end_point')
    print('working on ' + end_point)
    results = paginator(url1.format(end_point=end_point), querystring, headers)
    data = [{
            x: res[x]
            for x in elem['values']
            } for res in results]
    
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='id', inplace=True) 
    #spliting cretors-comics and comics
    df_creators_comics = df[['id', 'creators']]
    df = df[['id', 'title', 'modified']]
    #cleansing comics
    df = general_clean(df)
    df = elem.get('function')(df)        
    #save comics
    upsert_df_to_postgres(df=df, **elem.get('db'))
    

    #cleansing creators-comics
    elem = elements_to_extract.get('creator_comic')
    comics_creators = []
    for index, row in df_creators_comics.iterrows():
        comic_id = row['id']
        comics_creators += [get_comic_creator(comic_id, item) for item in  row['creators']['items']]
    df_creators_comics = pd.DataFrame(comics_creators)
    upsert_df_to_postgres(df=df_creators_comics, **elem.get('db'))
    


    querystring = {
            "apikey":"87a1c6ea5695c46726e54f9cf71322e3",
            "limit":100,
            "offset": 0,
            "orderBy": "-modified"
            }
    elem = elements_to_extract.get('characters')
    end_point = elem.get('end_point')
    print('working on ' + end_point)
    results = paginator(url1.format(end_point=end_point), querystring, headers)
    data = [{
            x: res[x]
            for x in elem['values']
            } for res in results]
    
    df = pd.DataFrame(data)
    df = general_clean(df)
    df = elem.get('function')(df)  
    df.drop_duplicates(subset='id', inplace=True)       
    upsert_df_to_postgres(df=df, **elem.get('db'))
    
    
    #get target avengers
    elem = elements_to_extract.get('target_characters')
    print('working on target_characters')
    df_ironman = df[df.name.str.contains('^(iron man)|^tony', case=False)]
    df_ironman['name'] = 'ironman'
    df_ironman = df_ironman[['name', 'id']]
    df_ironman.rename(columns={'id': 'character_id'}, inplace=True)

    df_cap = df[df.name.str.contains('^cap.*?ame', case=False)]
    df_cap['name'] = 'ironman'
    df_cap = df_cap[['name', 'id']]
    df_cap.rename(columns={'id': 'character_id'}, inplace=True)

    df_target = pd.concat([df_ironman, df_cap])
    upsert_df_to_postgres(df=df_target, **elem.get('db'))
    
    
    #get character-comics
    elem = elements_to_extract.get('comic_character')
    end_point = elem.get('end_point')
    url1 = url1.format(end_point=end_point)
    comics_character = []
    for character_id in df.id:
        querystring = {
        "apikey":"87a1c6ea5695c46726e54f9cf71322e3",
        "limit":100,
        "offset": 0,
        "orderBy": "-modified"
        }        
        
        print('working on ' + end_point + ': ' + str(character_id))
        results = paginator(url1.format(character_id=character_id), querystring, headers)
        data = [{
            x: res[x]
            for x in elem['values']
            } for res in results]
    
        df = pd.DataFrame(data)        
        df.rename(columns={'id': 'comic_id'}, inplace=True)
        if not df.empty:
            df['character_id'] = character_id
            comics_character.append(df)
    
    df_comic_char = pd.concat(comics_character)    
    upsert_df_to_postgres(df=df_comic_char, **elem.get('db'))    


if __name__ == '__main__':
    main()
