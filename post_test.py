'''
Created on May 9, 2017

@author: yingziwu
'''
import requests
import json

class post_test(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.base_headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04",  'Referer': 'https://v2ex.com/signin'}
        self.s=requests.session()
        self.s.headers=self.base_headers
        self.import_cookies()
        
    def import_cookies(self):
        with open('cookies.txt','r') as f:
            cookies=requests.utils.cookiejar_from_dict(json.load(f))
            self.s.cookies=cookies
        

if __name__ == '__main__':
    tmp=post_test()
    print('finish!')