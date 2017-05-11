'''
Created on May 9, 2017

@author: yingziwu
'''
import feedparser
import sqlite3
import time
import re
import requests
from redis import Redis
from rq import Queue
from v2ex_spider import topic_spider
import json
import os

class Rss_spider(object):
    '''
    A Spider for v2ex's Rss.
    Get the latest and hot topic on the index.
    Using the rss generate the topic list that need to spider.
    '''


    def __init__(self):
        '''
        >>>from v2ex_spider import rss_spider
        >>>rss_spider.Rss_spider()
        '''
        self.v2ex_rss_url_list=['https://www.v2ex.com/index.xml',
                   'https://www.v2ex.com/feed/tab/qna.xml',
                   'https://www.v2ex.com/feed/tab/jobs.xml',
                   'https://www.v2ex.com/feed/tab/deals.xml',
                   'https://www.v2ex.com/feed/tab/city.xml',
                   'https://www.v2ex.com/feed/tab/play.xml',
                   'https://www.v2ex.com/feed/tab/apple.xml',
                   'https://www.v2ex.com/feed/tab/creative.xml',
                   'https://www.v2ex.com/feed/tab/tech.xml']
        self.latest_hot_api=['https://www.v2ex.com/api/topics/latest.json','https://www.v2ex.com/api/topics/hot.json']
        self.topic_sleep_time=10
        self.SQ=SQL()
        self.SQ.open_datebase()
        self.redis_conn=Redis()
        #run
        self.latest_and_hot()
        self.gen_topic_queue()
        #end
        self.SQ.close_datebase()
    
    def topics_id_rss(self):
        topic_ids=list()
        for v2ex_rss_url in self.v2ex_rss_url_list:
            feed=feedparser.parse(v2ex_rss_url)
            items=feed["items"]
            for item in items:
                author=item["author"]
                title=item["title"]
                link=item["link"]
                published=item[ "date" ] 
                summary=item["summary"]
                topic_id=int(re.findall(r't\/(\d+)#?', link)[0])
                topic_ids.append(topic_id)
        topic_ids=set(topic_ids)
        return topic_ids

    def topics_id_sqlite(self):
        sql='SELECT ID FROM TOPIC;'
        self.SQ.cursor.execute(sql)
        topics_ids=[x[0] for x in self.SQ.cursor.fetchall()]
        return  topics_ids
    
    def latest_and_hot(self):
        for url in self.latest_hot_api:
            resp=requests.get(url)
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
        return


    def gen_topic_queue(self):
        topics_rss=self.topics_id_rss()
        topics_sql=self.topics_id_sqlite()
        if len(topics_sql) <= 2000:
            return
        # load topics
        if os.path.exists('.topics_all.json'):
            with open('.topics_all.json','r') as f:
                tmp_topics=json.load(f)
        else:
            tmp_topics=list()
        t_queue=Queue('topic',connection=self.redis_conn)
        # gen queue
        for topic in topics_rss:
            if topic not in topics_sql and topic not in tmp_topics:
                topic_id=int(topic)
                t_queue.enqueue(topic_spider.start,topic_id, self.topic_sleep_time)
        #save topics
        topics_all=list()
        topics_all.extend(topics_rss)
        topics_all.extend(topics_sql)
        with open('.topics_all.json','w') as f:
            json.dump(topics_all, f)
        return
              

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

if __name__ == '__main__':
    Rss_spider()
    print('Finish!')