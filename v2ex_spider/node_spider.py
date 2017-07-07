'''
Created on May 9, 2017

@author: yingziwu
'''
import logging

from v2ex_spider import base_spider
import settings

def start(node_id,sleep_time):
    logging.info('Start node spider. Node id is %d.' % int(node_id))
    url='https://www.v2ex.com/api/topics/show.json?node_id=%s' % str(node_id)
    base_spider.spider(url,sleep_time)
    return

if __name__ == '__main__':
    start(12,5)
    print('Finish!')