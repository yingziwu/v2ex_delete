'''
Created on May 12, 2017

@author: yingziwu
'''
import requests
import time
import logging

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
        logging.info('Start base spider. Url is %s' % url)
        self.url=url
        self.sleep_time=sleep_time
        time.sleep(int(self.sleep_time))
        self.SQ=SQL()
        self.SQ.open_datebase()
        #run
        self.load_config()
        self.spider()
        #end
        self.SQ.close_datebase()
        logging.info('Spider Finished.') 
        
    def spider(self):
        logging.debug('start spider.')
        try:
            resp=self.s.get(self.url, timeout=10)
        except requests.exceptions.RequestException as e:
            logging.error('spider failed.')
            logging.error('proxy_status: %s' % settings.proxy_enable)
            if settings.proxy_enable is True:
                logging.error('proxy: %s' % self.s.proxies)
            logging.error(e)
            raise e
        if resp.status_code != 200:
            self.SQ.close_datebase()
            error_info='proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies))
            logging.error('API Error: proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies)))
            raise APIError(error_info)
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
    
    def load_config(self):
        logging.debug('start load_config')
        self.proxy_enable=settings.proxy_enable
        self.s=requests.session()
        self.s.headers=settings.API_headers
        if self.proxy_enable:
            self.s.proxies=settings.proxies()
        return

class APIError(ValueError):
    pass
