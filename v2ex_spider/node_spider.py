'''
Created on May 9, 2017

@author: yingziwu
'''
from v2ex_spider import base_spider

def start(node_id,sleep_time):
    url='https://www.v2ex.com/api/topics/show.json?node_id=%s' % str(node_id)
    base_spider.spider(url,sleep_time)

if __name__ == '__main__':
    start(12,5)
    print('Finish!')