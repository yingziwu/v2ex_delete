CREATE TABLE TOPIC (
    ID INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    author_id INTEGER,
    content TEXT,
    content_rendered TEXT,
    replies INTEGER,
    node INTEGER,
    created INTEGER,
    time INTEGER
);

CREATE TABLE STATUS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    T_ID INTEGER,
    NODE INTEGER,
    STATUS INTEGER,
    TIME INTEGER
);

CREATE TABLE NODES (
    ID INTEGER PRIMARY KEY,
    name TEXT,
    url TEXT,
    title TEXT,
    title_alternative TEXT,
    topics INTEGER,
    header TEXT,
    footer TEXT,
    created INTEGER,
    time INTEGER
);
