'''
Created on May 9, 2017

@author: yingziwu
'''
import sqlite3
import requests
import time
import json

class Get_topics(object):
    '''
    A Spider for v2ex's node.
    Get a node's topics.
    '''    


    def __init__(self,node_id,sleep_time):
        '''
        >>>from v2ex_spider import node_spider
        >>>node_spider.start(12,5) ## node_spider.start(node_id,sleep_time)
        '''
        self.node_id=node_id
        self.sleep_time=sleep_time
        self.SQ=SQL()
        self.SQ.open_datebase()
        #run
        time.sleep(int(self.sleep_time))
        self.spider()
        #end
        self.SQ.close_datebase()    
        
    def spider(self):
        resp=requests.get('https://www.v2ex.com/api/topics/show.json?node_id=%s' % str(self.node_id))
        if resp.status_code != 200:
            self.SQ.close_datebase()
            raise APIError
        topics=resp.json()
        for topic in topics:
            t_id=topic["id"]
            title=topic["title"]
            author=topic["member"]["username"]
            author_id=topic["member"]["id"]
            content=topic["content"]
            content_rendered=topic["content_rendered"]
            replies=topic["replies"]
            node=topic["node"]["id"]
            created=topic["created"]
            n_time=int(time.time())
            self.SQ.write_to_db(t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time)
        self.SQ.conn.commit()

class SQL(object):
    def __init__(self):
        with open('config.json') as f:
            config_dict=json.load(f)
        self.database_path=config_dict["database_path"]

    def open_datebase(self):
        self.conn=sqlite3.connect(self.database_path)
        self.cursor=self.conn.cursor()

    def close_datebase(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def write_to_db(self,t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time):
        sql="INSERT INTO TOPIC (ID,title,author,author_id,content,content_rendered,replies,node,created,time) VALUES ( %s );" % ', '.join(['?'] * 10)
        try:
            self.cursor.execute(sql,(t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time))
        except sqlite3.IntegrityError as e:
            pass
class APIError(ValueError):
    pass

def start(node_id,sleep_time):
    Get_topics(node_id,sleep_time)

if __name__ == '__main__':
    start(12,5)
    print('Finish!')    