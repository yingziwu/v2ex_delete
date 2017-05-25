'''
Created on May 9, 2017

@author: yingziwu
'''
import json
import time
import requests
from v2ex_base import log_in
import os
from redis import Redis
from rq import Queue
from v2ex_spider import node_spider
from v2ex_spider import rss_spider
from v2ex_base.v2_sql import SQL
import settings
from v2ex_tester import topic_tester

class Start(object):
    '''
    Start the project.
    '''

    def __init__(self):
        '''
        $ python run.py
        or
        $ ./Run.sh
        '''
        self.SQ=SQL()
        self.SQ.open_datebase()
        self.redis_conn=Redis()
        self.load_config()
        #start
        self.load_json()
        self.update_cookies()
        try:
            self.update_nodes()
        except APIError as e:
            print(e)
        self.get_rss()
        self.tasker()
        self.tester_tasker()
        #end
        self.end()

    def end(self):
        self.SQ.close_datebase()
        self.dump_json()

    def load_json(self):
        #load .time_log.json
        if os.path.exists('.time_log.json'):
            with open('.time_log.json','r') as f:
                self.time_log=json.load(f)
        else:
            self.time_log={'cookies_time':'0','nodes_time':'0','8000_node':'0','4000_node':'0','1000_node':'0','500_node':'0','0_node':'0','rss_time':'0','tester':'0'}
        #load .node_number.json
        if os.path.exists('.node_number.json'):
            with open('.node_number.json','r') as f:
                self.node_number=json.load(f)
        else:
            self.node_number=list()
        return

    def dump_json(self):
        #dump .time_log.json
        with open('.time_log.json','w') as f1:
            json.dump(self.time_log, f1)
        #dump .node_number.json
        with open('.node_number.json','w') as f2:
            self.node_number=list(set(self.node_number))
            json.dump(self.node_number,f2)
        return

    def update_cookies(self):
        if int(time.time())-int(self.time_log["cookies_time"]) >= 86400:
            cookies_time_status = False
        else:
            cookies_time_status = True
        if not os.path.exists('cookies.txt') or cookies_time_status is False:
            try:
                log_s=log_in.v2ex_log_in()
                log_s.log_in()
                log_s.save_cookies()
            except log_in.LogError as e:
                print(e)
                return
            self.time_log["cookies_time"]=str(int(time.time()))
        return

    def update_nodes(self):
        if int(time.time())-int(self.time_log["nodes_time"]) >= 10800:
            nodes_time_status=False
        else:
            nodes_time_status=True
        if not nodes_time_status:
            resp=self.s.get('https://www.v2ex.com/api/nodes/all.json')
            if resp.status_code != 200:
                error_info='proxy status: %s, proxy: %s' % (str(settings.proxy_enable),str(self.s.proxies))
                raise APIError(error_info)
            nodes=resp.json()
            for node in nodes:
                n_id=node["id"]
                name=node["name"]
                url=node["url"]
                title=node["title"]
                title_alternative=node["title_alternative"]
                topics=node["topics"]
                header=node["header"]
                footer=node["footer"]
                created=node["created"]
                n_time=int(time.time())
                if self.SQ.node_test(n_id, topics) is True:
                    self.node_number.append(int(n_id))
                self.SQ.write_to_db_node(n_id, name, url, title, title_alternative, topics, header, footer, created, n_time)
            self.time_log["nodes_time"]=str(int(time.time()))
        self.node_number=list(set(self.node_number))
        return

    def tasker(self):
        node_configs_1=[{'sql':'SELECT ID FROM NODES WHERE topics >= 8000;','sleep_time':5,'between_time':900,'time_log':'8000_node','queue_name':'node1'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 3000 AND 8000;','sleep_time':10,'between_time':1800,'time_log':'4000_node','queue_name':'node2'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 1000 AND 3000;','sleep_time':20,'between_time':7200,'time_log':'1000_node','queue_name':'node3'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 100 AND 1000;','sleep_time':90,'between_time':86400,'time_log':'500_node','queue_name':'node4'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 1 AND 100;','sleep_time':90,'between_time':86400,'time_log':'0_node','queue_name':'node5'}]
        node_configs_2=[{'sql':'SELECT ID FROM NODES WHERE topics >= 8000;','sleep_time':5,'between_time':1800,'time_log':'8000_node','queue_name':'node1'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 3000 AND 8000;','sleep_time':10,'between_time':3600,'time_log':'4000_node','queue_name':'node2'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 1000 AND 3000;','sleep_time':20,'between_time':14400,'time_log':'1000_node','queue_name':'node3'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 100 AND 1000;','sleep_time':90,'between_time':86400,'time_log':'500_node','queue_name':'node4'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 1 AND 100;','sleep_time':90,'between_time':86400,'time_log':'0_node','queue_name':'node5'}]
        time.tzname=('CST', 'CST')
        if int(time.strftime('%H')) >= 8 or int(time.strftime('%H')) < 2:
            node_configs=node_configs_1
        else:
            node_configs=node_configs_2
        for node_config in node_configs:
            sql=node_config['sql']
            sleep_time=node_config['sleep_time']
            between_time=node_config['between_time']
            time_log_name=node_config['time_log']
            queue_name=node_config['queue_name']
            q_node=Queue(queue_name,connection=self.redis_conn)
            if int(time.time()) - int(self.time_log[time_log_name]) >= between_time:
                self.SQ.cursor.execute(sql)
                node_ids=self.SQ.cursor.fetchall()
                for node_id in node_ids:
                    if queue_name != 'node5' or (queue_name == 'node5' and node_id in self.node_number):
                        node_id=node_id[0]
                        if queue_name == 'node5':
                            self.node_number.remove(int(node_id))
                        q_node.enqueue(node_spider.start,node_id,sleep_time)
                self.time_log[time_log_name]=str(int(time.time()))
        return

    def get_rss(self):
        if int(time.time())-int(self.time_log["rss_time"]) >= 600:
            rss_spider.Rss_spider()
            self.time_log["rss_time"]=str(int(time.time()))
        return

    def load_config(self):
        self.proxy_enable=settings.proxy_enable
        self.s=requests.session()
        self.s.headers=settings.API_headers
        if self.proxy_enable:
            self.s.proxies=settings.proxies
        return

    def tester_tasker(self):
        if int(time.time())-int(self.time_log["tester"]) >= 1800:
            #losd json
            if os.path.exists('.topics_tester.json'):
                with open('.topics_tester.json','r') as f:
                    tmp_topics=json.load(f)
            else:
                tmp_topics=list()
            #main
            sql="SELECT ID FROM TOPIC WHERE (time - created) < 345600 AND ID NOT IN (SELECT T_ID FROM STATUS) AND (STRFTIME('%s','now') - created) > 1209600;"
            sleep_time=20
            self.SQ.cursor.execute(sql)
            topic_ids=[x[0] for x in self.SQ.cursor.fetchall()]
            q=Queue('tester',connection=self.redis_conn)
            for topic_id in topic_ids:
                if topic_id not in tmp_topics:
                    q.enqueue(topic_tester.start,topic_id, sleep_time)
                    tmp_topics.append(topic_id)
            #end
            tmp_topics=list(set(tmp_topics))
            with open('.topics_tester.json','w') as f:
                json.dump(tmp_topics,f)
            self.time_log["tester"]=str(int(time.time()))
        return

class APIError(ValueError):
    pass

if __name__ == '__main__':
    S=Start()
    print('Finsh!')
