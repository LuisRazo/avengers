import psycopg2
import os

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
CREATE TABLE comics(
    id INT PRIMARY KEY,
    title TEXT,
    modified TIMESTAMP,
    created TIMESTAMP
);

CREATE TABLE characters(
    id INT PRIMARY KEY,
    name TEXT,
    modified TIMESTAMP,
    created TIMESTAMP
);

CREATE TABLE creators(
    id INT PRIMARY KEY,
    full_name TEXT,
    modified TIMESTAMP,
    created TIMESTAMP
);

CREATE TABLE character_comic(
    comic_id INT REFERENCES comics(id),
    character_id INT REFERENCES characters(id),
    PRIMARY KEY (comic_id, character_id)
);

CREATE TABLE creator_comic(
    comic_id INT REFERENCES comics(id),
    creator_id INT REFERENCES creators(id),
    role TEXT,
    PRIMARY KEY (comic_id, creator_id)
);

CREATE TABLE target_characters(
    name TEXT PRIMARY KEY,
    character_id INT REFERENCES characters(id)
);
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(
          host=os.environ['RDS_HOSTNAME'],
          port=os.environ['RDS_PORT'],
          user=os.environ['RDS_USERNAME'],
          dbname=os.environ['RDS_DBNAME'],
          password=os.environ['RDS_PASSWORD']
        )
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def lambda_handler(event, context):
    print(event)