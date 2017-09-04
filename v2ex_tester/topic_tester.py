'''
Created on May 9, 2017

@author: yingziwu
'''
import requests
import json
from lxml import etree
import time
import re
import logging

from v2ex_base.v2_sql import SQL
import settings

class tester(object):
    '''
    The tester for v2ex topics.
    '''


    def __init__(self):
        '''
        >>>from v2ex_tester import topic_tester
        >>>topic_tester(topic_id,sleep_time)
        '''
        logging.debug('init class tester')
        self.s=requests.session()
        if settings.proxy_enable is True:
            self.s.proxies=settings.proxies()
        self.s.headers=settings.WEB_headers
        self.log_status=False
    
    def init_database(self):
        logging.debug('init database')
        self.SQ=SQL()
        self.SQ.open_datebase()
     
    def log_in(self):
        logging.debug('log in account')
        with open('.cookies.json','r') as f:
            cookies=requests.utils.cookiejar_from_dict(json.load(f))
            self.s.cookies=cookies
        self.s.headers=settings.WEB_headers
        self.log_status=True
        return
    
    def web_test(self,t_id,status):
        logging.debug('Start web_test')
        url='https://www.v2ex.com/t/%s' % str(t_id)
        n_time=int(time.time())
        try:
            resp=self.s.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            logging.error('web_test failed.')
            logging.error('proxy_status: %s' % settings.proxy_enable)
            if settings.proxy_enable is True:
                logging.error('proxy: %s' % self.s.proxies)
            logging.error(e)
            raise e
        if resp.status_code == 403:
            error_info='proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies))
            logging.error('API Error: proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies)))
            raise APIError(error_info)
        if resp.status_code == 404 and '404 Topic Not Found' in resp.text :
            return {'T_ID':int(t_id),'NODE':None,'STATUS':3,'TIME':n_time}
        if resp.url == 'https://www.v2ex.com/':
            return self.api_test(t_id, status=2)
        if 'signin' in resp.url and self.log_status is False:
#             self.log_in()
#             return self.web_test(t_id, status=1)
            return self.api_test(t_id, status=1)
        tree=etree.HTML(resp.text)
        node_name=re.findall(r'\/go\/(\w+)', tree.xpath('//div[@class="header"]/a[2]/@href')[0])[0]
        self.SQ.cursor.execute("SELECT ID FROM NODES WHERE name == '%s';" % node_name)
        node_id=self.SQ.cursor.fetchone()[0]
        return {'T_ID':int(t_id),'NODE':node_id,'STATUS':status,'TIME':n_time}
    
    def api_test(self,t_id,status):
        logging.debug('Start api_test')
        self.s_a=requests.session()
        if settings.proxy_enable is True:
            self.s_a.proxies=settings.proxies()
        self.s_a.headers=settings.API_headers
        url='https://www.v2ex.com/api/topics/show.json?id=%s' % str(t_id)
        n_time=int(time.time())
        try:
            resp=self.s_a.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            logging.error('api_test failed.')
            logging.error('proxy_status: %s' % settings.proxy_enable)
            if settings.proxy_enable is True:
                logging.error('proxy: %s' % self.s.proxies)
            logging.error(e)
            raise e
        if resp.status_code != 200:
            error_info='proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies))
            logging.error('API Error: proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies)))
            raise APIError(error_info)
        if len(resp.json()) == 0:
            return {'T_ID':int(t_id),'NODE':None,'STATUS':3,'TIME':n_time}
        topic=resp.json()[0]
        node_id=topic["node"]["id"]
        return {'T_ID':int(t_id),'NODE':node_id,'STATUS':status,'TIME':n_time}
    
    def write_to_sql(self,T_ID, NODE, STATUS, TIME):
        self.SQ.write_to_db_status(T_ID, NODE, STATUS, TIME)
        return

class APIError(ValueError):
    pass
    
def start(t_id,sleep_time):
    logging.info('Start topic test. Topic id is %d.' % int(t_id))
    time.sleep(sleep_time)
    t=tester()
    t.init_database()
    result=t.web_test(t_id, 0)
    t.write_to_sql(result['T_ID'],result['NODE'],result['STATUS'],result['TIME'])
    t.SQ.close_datebase()
    if result['NODE'] is not None:
        logging.info('Topic test finish. Topic id is %d, results is : node id %d, status %d' % (int(t_id),result['NODE'],result['STATUS']))
    else:
        logging.info('Topic test finish. Topic id is %d, results is : node id is None, status %d' % (int(t_id),result['STATUS']))
    return

if __name__ == '__main__':
#     start(1,5)
    start(375807,5)
    print('finish!')