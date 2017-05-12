'''
Created on May 12, 2017

@author: arch
'''
import settings
import sqlite3

class SQL(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.database_path=settings.database_path

    def open_datebase(self):
        self.conn=sqlite3.connect(self.database_path)
        self.cursor=self.conn.cursor()

    def close_datebase(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def write_to_db_base(self,t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time):
        sql="INSERT INTO TOPIC (ID,title,author,author_id,content,content_rendered,replies,node,created,time) VALUES ( %s );" % ', '.join(['?'] * 10)
        try:
            self.cursor.execute(sql,(t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time))
        except sqlite3.IntegrityError as e:
            pass