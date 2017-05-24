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

CREATE VIEW HUMAN_READER AS
SELECT TOPIC.ID,TOPIC.title,TOPIC.author,TOPIC.author_id,TOPIC.content,TOPIC.content_rendered,TOPIC.replies,
NODES_1.name AS node_name,TOPIC.node AS node_id,
TOPIC.created AS create_time,DATETIME(TOPIC.created,'unixepoch') AS create_time_h,TOPIC.time AS grab_time,DATETIME(TOPIC.time,'unixepoch') AS grab_time_h,
STATUS.TIME AS test_time,DATETIME(STATUS.TIME,'unixepoch') AS test_time_h,STATUS.NODE AS node_id_on_test,NODES_2.name AS node_name_on_test,STATUS.STATUS
FROM TOPIC
INNER JOIN NODES AS NODES_1
ON NODES_1.ID = TOPIC.node
LEFT OUTER JOIN STATUS
ON STATUS.T_ID = TOPIC.ID
LEFT OUTER JOIN NODES AS NODES_2
ON NODES_2.ID = STATUS.NODE
ORDER BY TOPIC.ID ASC;
