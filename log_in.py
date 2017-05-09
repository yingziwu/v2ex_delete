'''
Created on May 9, 2017

@author: yingziwu
'''

import requests
from lxml import etree
import json
import os

class v2ex_log_in(object):
    '''
    log in v2ex account,return the cookies.
    '''


    def __init__(self):
        '''
        log in v2ex account,return the cookies.
        '''
        self.load_config()
        self.s=requests.session()
        self.s.headers=self.base_headers
        return
    
    def load_config(self):
        if os.path.exists('v2ex_config.json'):
            with open('v2ex_config.json','r') as f:
                config=json.load(f)
                self.account=config["account"]
                self.passwd=config["password"]
                self.base_headers=config["base_headers"]
        else:
            raise FileExistsError

    def log_in(self):
        #1
        r1=self.s.get('https://www.v2ex.com/signin')
        t1=etree.HTML(r1.text)
        text_name=t1.xpath('//input[@type="text"]/@name')[-1]
        password_name=t1.xpath('//input[@type="password"]/@name')[0]
        once1=t1.xpath('//input[@type="hidden"]/@value')[0]
        post_data={text_name:self.account, password_name:self.passwd, 'once':str(once1), 'next':'/'}
        #r2
        r2=self.s.post('https://www.v2ex.com/signin', data=post_data)
        return
        
    def save_cookies(self):
        resp=self.s.get('https://www.v2ex.com/go/flamewar')
        if '登录' in resp.text:
            raise LogError('log failed.')
        with open('cookies.txt','w') as f:
            json.dump(requests.utils.dict_from_cookiejar(self.s.cookies),f)
        return
            
class LogError(ValueError):
    pass
    
if __name__ == '__main__':
    tmp=v2ex_log_in()
    tmp.log_in()
    tmp.save_cookies()
    print('finish!')
    