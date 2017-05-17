'''
Created on May 9, 2017

@author: yingziwu
'''
import requests
import json
import settings
from lxml import etree
import time
import re
from v2ex_base.v2_sql import SQL

class tester(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.s=requests.session()
        self.s.proxies=settings.proxies
        self.SQ=SQL()
        self.SQ.open_datebase()
        self.s.headers=settings.WEB_headers
        self.log_status=False
        
    def log_in(self):
        with open('.cookies.json','r') as f:
            cookies=requests.utils.cookiejar_from_dict(json.load(f))
            self.s.cookies=cookies
        self.s.headers=settings.WEB_headers_list[0]
        return
    
    def web_test(self,t_id,status):
        url='https://www.v2ex.com/t/%s' % str(t_id)
        n_time=int(time.time())
        resp=self.s.get(url)
        if '404 Topic Not Found' in resp.text:
            return {'T_ID':int(t_id),'NODE':None,'STATUS':3,'TIME':n_time}
        if resp.url == 'https://www.v2ex.com/':
            return self.api_test(t_id, status=2)
        if 'signin' in resp.url and self.log_status is False:
            self.log_in()
            return self.web_test(t_id, status=1)
        tree=etree.HTML(resp.text)
        node_name=re.findall(r'\/go\/(\w+)', tree.xpath('//div[@class="header"]/a[2]/@href')[0])[0]
        self.SQ.cursor.execute("SELECT ID FROM NODES WHERE name == '%s';" % node_name)
        node_id=self.SQ.cursor.fetchone()[0]
        return {'T_ID':int(t_id),'NODE':node_id,'STATUS':status,'TIME':n_time}
    
    def api_test(self,t_id,status): 
        self.s_a=requests.session() 
        self.s_a.proxies=settings.proxies
        self.s_a.headers=settings.API_headers
        url='https://www.v2ex.com/api/topics/show.json?id=%s' % str(t_id)
        n_time=int(time.time())
        resp=self.s_a.get(url)
        topic=resp.json()[0]
        node_id=topic["node"]["id"]
        return {'T_ID':int(t_id),'NODE':node_id,'STATUS':status,'TIME':n_time}
    
    def write_to_sql(self,T_ID, NODE, STATUS, TIME):
        self.SQ.write_to_db_status(T_ID, NODE, STATUS, TIME)
        return
    
def start(t_id,sleep_time):
    time.sleep(sleep_time)
    t=tester()
    result=t.web_test(t_id, 0)
    t.write_to_sql(result['T_ID'],result['NODE'],result['STATUS'],result['TIME'])
    t.SQ.close_datebase()
    return

if __name__ == '__main__':
    start(1,5)
    print('finish!')