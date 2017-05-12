'''
Created on May 10, 2017

@author: yingziwu
'''
from v2ex_spider import base_spider

def start(topic_id, sleep_time):
    url='https://www.v2ex.com/api/topics/show.json?id=%s' % str(topic_id)
    base_spider.spider(url,sleep_time)
    return

if __name__ == '__main__':
    start(1,5)
    print('Finish!')