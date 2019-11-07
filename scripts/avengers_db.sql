CREATE TABLE comics(
    id INT PRIMARY KEY,
    title TEXT,
    modified TIMESTAMP
);

CREATE TABLE characters(
    id INT PRIMARY KEY,
    name TEXT,
    modified TIMESTAMP
);

CREATE TABLE creators(
    id INT PRIMARY KEY,
    full_name TEXT,
    modified TIMESTAMP
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
    name TEXT,
    character_id INT REFERENCES characters(id),
    PRIMARY KEY (name,character_id)
);