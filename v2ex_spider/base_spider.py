'''
Created on May 12, 2017

@author: yingziwu
'''
import requests
import time
from v2ex_base.v2_sql import SQL
import settings

class spider(object):
    '''
    A base Spider for v2ex.
    '''    


    def __init__(self,url,sleep_time):
        '''
        >>>from v2ex_spider import base_spider
        >>>base_spider.start(url,sleep_time)
        '''
        self.url=url
        self.sleep_time=sleep_time
        self.SQ=SQL()
        self.SQ.open_datebase()
        #run
        time.sleep(int(self.sleep_time))
        self.load_config()
        self.spider()
        #end
        self.SQ.close_datebase()    
        
    def spider(self):
        resp=self.s.get(self.url)
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
            self.SQ.write_to_db_base(t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time)
        self.SQ.conn.commit()
    
    def load_config(self):
        self.proxy_enable=settings.proxy_enable
        self.s=requests.session()
        self.s.headers=settings.API_headers
        if self.proxy_enable:
            self.s.proxies=settings.proxies

class APIError(ValueError):
    pass
