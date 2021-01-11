from be.model import store

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker
import psycopg2


class DBConn:
    def __init__(self):
        self.conn = store.Store.__init__(self)
    def user_id_exist(self, user_id):
        cursor = self.conn.execute("SELECT user_id FROM usr WHERE user_id ='%s';"%(user_id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.conn.execute("SELECT book_id FROM store WHERE store_id = '%s' AND book_id = '%s';"%(store_id, book_id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.conn.execute("SELECT store_id FROM user_store WHERE store_id = '%s';"%(store_id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
