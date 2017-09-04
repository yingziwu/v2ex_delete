'''
Created on May 9, 2017

@author: yingziwu
'''

import requests
from lxml import etree
import json
import logging

import settings

class v2ex_log_in(object):
    '''
    log in v2ex account,return the cookies.
    '''


    def __init__(self):
        '''
        >>>import log_in
        >>>log_s=log_in.v2ex_log_in()
        >>>log_s.log_in()
        >>>log_s.save_cookies()
        '''
        logging.info('start log in')
        self.load_config()       
        return
    
    def load_config(self):
        logging.debug('start load_config')
        self.account=settings.account
        self.passwd=settings.password
        self.proxy_enable=settings.i_proxy_enable
        self.base_headers=settings.WEB_headers
        self.s=requests.session()
        self.s.headers=self.base_headers
        if self.proxy_enable:
            self.s.proxies=settings.i_proxies()
        return

    def log_in(self,try_time):
        logging.debug('start log_in')
        if try_time >= 4:
            logging.error(LogError('try time too much.'))
            raise LogError('try time too much.')
        #1
        try:
            r1=self.s.get('https://www.v2ex.com/signin', timeout=10)
        except requests.exceptions.RequestException as e:
            logging.error('log in error')
            logging.error(try_time)
            logging.error('proxy status: %s' % self.proxy_enable)
            if self.proxy_enable is True:
                logging.error('proxy: %s' % self.s.proxies)
            logging.error(e)
            try_time=try_time+1
            return self.log_in(try_time)
        if r1.status_code != 200:
            error_info='proxy status: %s, proxy: %s' % (str(settings.i_proxy_enable),str(self.s.proxies))
            raise LogError(error_info)
        self.s.headers={'Referer': 'https://v2ex.com/signin'}
        t1=etree.HTML(r1.text)
        text_name=t1.xpath('//input[@type="text"]/@name')[-1]
        password_name=t1.xpath('//input[@type="password"]/@name')[0]
        once1=t1.xpath('//input[@type="hidden"]/@value')[0]
        post_data={text_name:self.account, password_name:self.passwd, 'once':str(once1), 'next':'/'}
        #r2
        try:
            r2=self.s.post('https://www.v2ex.com/signin', data=post_data)
        except requests.exceptions.RequestException as e:
            logging.error('log in error')
            logging.error(try_time)
            logging.error('proxy status: %s' % self.proxy_enable)
            if self.proxy_enable is True:
                logging.error('proxy: %s' % self.s.proxies)
            logging.error(e)
            try_time=try_time+1
            return self.log_in(try_time)            
        return
        
    def save_cookies(self):
        logging.debug('start save_cookies')
        resp=self.s.get('https://www.v2ex.com/go/flamewar', timeout=10)
        if '登录' in resp.text:
            raise LogError('log failed.')
        with open('.cookies.json','w') as f:
            json.dump(requests.utils.dict_from_cookiejar(self.s.cookies),f)
        return
            
class LogError(ValueError):
    pass
    
if __name__ == '__main__':
    tmp=v2ex_log_in()
    tmp.log_in(1)
    tmp.save_cookies()
    print('finish!')
    