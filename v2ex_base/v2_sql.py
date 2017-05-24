'''
Created on May 12, 2017

@author: yingziwu
'''
import settings
import sqlite3

class SQL(object):
    '''
    The sqlite class.
    '''


    def __init__(self):
        '''
        >>>from v2ex_base.v2_sql import SQL
        >>>SQ=SQL()
        >>>SQ.open_datebase()
        write_to_db_base
        >>>SQ.write_to_db_base(t_id,title,author,author_id,content,content_rendered,replies,node,created,n_time)
        write_to_db_node
        >>>SQ.write_to_db_node(n_id,name,url,title,title_alternative,topics,header,footer,created,n_time)
        node_test
        >>>SQ.node_test(node_id,number_now)
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
        self.conn.commit()
        return

    def write_to_db_node(self,n_id,name,url,title,title_alternative,topics,header,footer,created,n_time):
        sql="REPLACE INTO NODES (ID,name,url,title,title_alternative,topics,header,footer,created,time) VALUES ( %s );" % ', '.join(['?'] * 10)
        try:
            self.cursor.execute(sql, (n_id,name,url,title,title_alternative,topics,header,footer,created,n_time))
        except sqlite3.IntegrityError as e:
            pass
        self.conn.commit()
        return

    def write_to_db_status(self,T_ID,NODE,STATUS,TIME):
        sql="INSERT INTO STATUS (T_ID,NODE,STATUS,TIME) VALUES ( %s );" % ', '.join(['?'] * 4)
        try:
            self.cursor.execute(sql,(T_ID,NODE,STATUS,TIME))
        except sqlite3.IntegrityError as e:
            pass
        self.conn.commit()
        return

    def node_test(self,node_id,number_now):
        sql="SELECT topics FROM NODES WHERE ID = %d;" % int(node_id)
        self.cursor.execute(sql)
        number_old_r=self.cursor.fetchone()
        if number_old_r is None:
            return True
        else:
            number_old=number_old_r[0]
        if int(number_old) != int(number_now):
            return True
        else:
            return False
