'''
Created on May 9, 2017

@author: yingziwu
'''
import feedparser
import os
import log_in
import sqlite3
import time
import re

def get_rss_detail():
    v2ex_rss_url_list=['https://www.v2ex.com/index.xml',
                       'https://www.v2ex.com/feed/tab/qna.xml',
                       'https://www.v2ex.com/feed/tab/jobs.xml',
                       'https://www.v2ex.com/feed/tab/deals.xml',
                       'https://www.v2ex.com/feed/tab/city.xml',
                       'https://www.v2ex.com/feed/tab/play.xml',
                       'https://www.v2ex.com/feed/tab/apple.xml',
                       'https://www.v2ex.com/feed/tab/creative.xml',
                       'https://www.v2ex.com/feed/tab/tech.xml']
    for v2ex_rss_url in v2ex_rss_url_list:
        feed=feedparser.parse(v2ex_rss_url)
        items=feed["items"]
        for item in items:
            author=item["author"]
            title=item["title"]
            link=item["link"]
            published=item[ "date" ] 
            summary=item["summary"]
            SQ.feed2sql(author,title,link,published,summary)
        SQ.conn.commit()

def update_cookies():
    time_now=int(time.time())
    if os.path.exists('time_test.txt'):
        with open('time_test.txt','r') as f:
            if time_now-int(f.read()) >= 86400:
                time_status = False
            else:
                time_status = True        
    if not os.path.exists('cookies.txt') or not os.path.exists('time_test.txt') or time_status is False:
        log_s=log_in.v2ex_log_in()
        log_s.log_in()
        log_s.save_cookies()
        with open('time_test.txt','w') as f:
            f.write(str(time_now))
        return

class SQL(object):
    def open_datebase(self):
        self.conn=sqlite3.connect('database.db')
        self.cursor=self.conn.cursor()

    def close_datebase(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def feed2sql(self,author,title,link,published,summary):
        post_id=re.findall(r't\/(\d+)#?', link)[0]
        timesteamp=time.strftime('%s',(time.strptime(re.sub('Z','+0800',published), '%Y-%m-%dT%H:%M:%S%z')))
        sql="INSERT INTO FEED (ID,title,author,summary,time) VALUES (?,?,?,?,?);"
        try:
            self.cursor.execute(sql,(post_id,title,author,summary,timesteamp))
        except sqlite3.IntegrityError as e:
            pass

if __name__ == '__main__':
    SQ=SQL()
    SQ.open_datebase()
    update_cookies()
    get_rss_detail()

    