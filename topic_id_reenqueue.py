'''
Created on Jun 10, 2017

@author: arch
'''
from redis import Redis
from rq import Queue
import sqlite3
import os
import json
import logging

from v2ex_spider import topic_spider
import settings

sql="select ID from TOPIC;"
conn=sqlite3.connect(settings.database_path)
cursor=conn.cursor()
cursor.execute(sql)
r=cursor.fetchall() 
ids_db=[int(x[0]) for x in r]
max_id=max(ids_db)
cursor.close()
conn.commit()
conn.close()

redis_conn=Redis()
q=Queue('topic',connection=redis_conn)

def reenqueue_m(start_id,end_id):
    #load topic id
    if os.path.exists('.topics_all.json'):
        with open('.topics_all.json','r') as f:
            tmp_topics=json.load(f)
    else:
        tmp_topics=list()
    #work
    for x in range(int(start_id),int(end_id)+1):                                   
        if x not in ids_db and x not in tmp_topics:
            logging.info('enqueue the topic %d' % int(x))
            q.enqueue(topic_spider.start,x, 10)
            tmp_topics.append(int(x))
    #save topic id
    topics_all=list()
    topics_all.extend(ids_db)
    topics_all.extend(tmp_topics)
    topics_all=list(set(topics_all))
    with open('.topics_all.json','w') as f:
        json.dump(topics_all, f)
    return

def reenqueue_a():
    start_id=max_id-2000
    end_id=max_id-150
    return reenqueue_m(start_id, end_id)

if __name__ == '__main__':
    import sys
    args=sys.argv
    if len(args) < 3 and (len(args) != 3 and args[1] != 'auto'):
        print('Please input the topic id of start and end.')
        print('Or use the auto mode.')
        exit(2)
    elif len(args) != 3 and args[1] == 'auto':
        reenqueue_a()
        print('auto')
    elif len(args) == 3:
        start_id=args[1]
        end_id=args[2]
        print('manual')
        reenqueue_m(start_id, end_id)
    print('Finish!')