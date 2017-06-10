'''
Created on Jun 10, 2017

@author: arch
'''
from redis import Redis
from rq import Queue
import sqlite3
import sys

from v2ex_spider import topic_spider

sql="select ID from TOPIC;"
conn=sqlite3.connect('/home/arch/python/v2ex_delete/database.db')
cursor=conn.cursor()
cursor.execute(sql)
r=cursor.fetchall() 
ids_db=[int(x[0]) for x in r]
max_id=max(ids_db)

redis_conn=Redis()
q=Queue('topic',connection=redis_conn)

def reenqueue_m(start_id,end_id):
    for x in range(int(start_id),int(end_id)+1):                                   
        if x not in ids_db:
            print(x)
            q.enqueue(topic_spider.start,x, 10)
    return

def reenqueue_a():
    start_id=max_id-2000
    end_id=max_id-150
    return reenqueue_m(start_id, end_id)

if __name__ == '__main__':
    args=sys.argv
    if len(args) != 3 and args[1] != 'auto':
        print('Please input the topic id of start and end.')
        print('Or use the auto mode.')
        exit(2)
    elif len(args) != 3 and args[1] == 'auto':
        reenqueue_a()
    elif len(args) == 3:
        start_id=args[1]
        end_id=args[2]
        reenqueue_m(start_id, end_id)
    print('Finish!')