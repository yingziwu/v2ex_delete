'''
Created on May 9, 2017

@author: yingziwu
'''
import feedparser
import time
import re
import requests
from redis import Redis
from rq import Queue
import json
import os
import logging

from v2ex_spider import topic_spider
from v2ex_base.v2_sql import SQL
import settings


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
        logging.info('start Rss spider')
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
        logging.debug('open sql database')
        self.SQ=SQL()
        self.SQ.open_datebase()
        self.redis_conn=Redis()
        self.load_config()
        #run
        try:
            self.latest_and_hot()
        except APIError as e:
            pass
        self.gen_topic_queue()
        #end
        self.SQ.close_datebase()
        logging.info('end the Rss spider')
    
    def topics_id_rss(self):
        logging.debug('fetch rss feeds')
        topic_ids=list()
        for v2ex_rss_url in self.v2ex_rss_url_list:
            feed=feedparser.parse(v2ex_rss_url)
            logging.debug('fetch rss feed: %s' % v2ex_rss_url)
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
        logging.debug('SELECT ID FROM TOPIC')
        sql='SELECT ID FROM TOPIC;'
        self.SQ.cursor.execute(sql)
        topics_ids=[x[0] for x in self.SQ.cursor.fetchall()]
        return  topics_ids
    
    def latest_and_hot(self):
        logging.debug('start latest_and_hot')
        for url in self.latest_hot_api:
            try:
                resp=self.s.get(url, timeout=10)
            except requests.exceptions.RequestException as e:
                logging.error('latest_and_hot error')
                logging.error('proxy_status: %s' % self.proxy_enable)
                if self.proxy_enable is True:
                    logging.error('proxy: %s' % self.s.proxies)
                logging.error(e)
                raise e
            if resp.status_code != 200:
                logging.error('latest_and_hot error')
                logging.error('proxy_status: %s' % self.proxy_enable)
                if self.proxy_enable is True:
                    logging.error('proxy: %s' % self.s.proxies)
                logging.error(APIError('latest_and_hot'))
                raise APIError('latest_and_hot')
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
                self.SQ.write_to_db_base(t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time)
            self.SQ.conn.commit()
        return

    def gen_topic_queue(self):
        logging.debug('start topic enqueue')
        topics_sql=self.topics_id_sqlite()
        if len(topics_sql) <= 2000:
            return
        topics_rss=self.topics_id_rss()
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
        topics_all.extend(tmp_topics)
        topics_all.extend(topics_rss)
        topics_all.extend(topics_sql)
        topics_all=list(set(topics_all))
        with open('.topics_all.json','w') as f:
            json.dump(topics_all, f)
        return

    def load_config(self):
        logging.debug('load config')
        self.proxy_enable=settings.i_proxy_enable
        self.s=requests.session()
        self.s.headers=settings.API_headers
        if self.proxy_enable:
            self.s.proxies=settings.i_proxies()

class APIError(ValueError):
    pass

if __name__ == '__main__':
    Rss_spider()
    print('Finish!')