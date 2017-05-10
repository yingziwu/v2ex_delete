'''
Created on May 9, 2017

@author: yingziwu
'''
import json
import time
import sqlite3
import requests
import log_in
import os
from redis import Redis
from rq import Queue
from node_spider import start

class Start(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.SQ=SQL()
        self.SQ.open_datebase()
        self.redis_conn=Redis()
        #start
        self.load_time_json()
        self.update_cookies()
        self.update_nodes()
        self.tasker()
        #end
        self.SQ.close_datebase()
        with open('time_log.json','w') as f:
            json.dump(self.time_log, f)
        
    def load_time_json(self):
        if os.path.exists('time_log.json'):
            with open('time_log.json','r') as f:
                self.time_log=json.load(f)
        else:
            self.time_log={'cookies_time':'0','nodes_time':'0','8000_node':'0','4000_node':'0','1000_node':'0','500_node':'0','0_node':'0'}
        return

    def update_cookies(self):
        if int(time.time())-int(self.time_log["cookies_time"]) >= 86400:
            cookies_time_status = False
        else:
            cookies_time_status = True        
        if not os.path.exists('cookies.txt') or cookies_time_status is False:
            log_s=log_in.v2ex_log_in()
            log_s.log_in()
            log_s.save_cookies()
            self.time_log["cookies_time"]=str(int(time.time()))
        return
    
    def update_nodes(self):
        if int(time.time())-int(self.time_log["nodes_time"]) >= 432000:
            nodes_time_status=False
        else:
            nodes_time_status=True
        if not nodes_time_status:
            resp=requests.get('https://www.v2ex.com/api/nodes/all.json')
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
                sql="INSERT INTO NODES (ID,name,url,title,title_alternative,topics,header,footer,created) VALUES ( %s );" % ', '.join(['?'] * 9)
                try:
                    self.SQ.cursor.execute(sql, (n_id,name,url,title,title_alternative,topics,header,footer,created))
                except sqlite3.IntegrityError as e:
                    pass
            self.SQ.conn.commit()
            self.time_log["nodes_time"]=str(int(time.time()))
        return
        
    def tasker(self):
        node_configs=[{'sql':'SELECT ID FROM NODES WHERE topics >= 8000;','sleep_time':5,'between_time':900,'time_log':'8000_node','queue_name':'node1'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 4000 AND 8000;','sleep_time':10,'between_time':1800,'time_log':'4000_node','queue_name':'node2'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 1000 AND 4000;','sleep_time':15,'between_time':18000,'time_log':'1000_node','queue_name':'node3'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 500 AND 1000;','sleep_time':120,'between_time':345600,'time_log':'500_node','queue_name':'node4'},
                      {'sql':'SELECT ID FROM NODES WHERE topics BETWEEN 1 AND 500;','sleep_time':180,'between_time':691200,'time_log':'0_node','queue_name':'node5'}]
        for node_config in node_configs:
            sql=node_config['sql']
            sleep_time=node_config['sleep_time']
            between_time=node_config['between_time']
            time_log_name=node_config['time_log']
            q_node=Queue(node_config['queue_name'],connection=self.redis_conn)
            if int(time.time()) - int(self.time_log[time_log_name]) >= between_time:
                self.SQ.cursor.execute(sql)
                node_ids=self.SQ.cursor.fetchall()
                for node_id in node_ids:
                    node_id=node_id[0]
                    q_node.enqueue(start,node_id,sleep_time)
                self.time_log[time_log_name]=str(int(time.time()))
        return
        

class SQL(object):
    def open_datebase(self):
        self.conn=sqlite3.connect('database.db')
        self.cursor=self.conn.cursor()

    def close_datebase(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    S=Start()
    print('Finsh!')
