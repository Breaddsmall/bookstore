import logging
import os
import sqlite3 as sqlite

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

import psycopg2


class Store:
    def __init__(self):
        # 连接数据库legend 记得修改这个！！！
        # engine = create_engine(Conf.get_sql_conf('local_w'))
        url = 'postgresql://{}:{}@{}:{}/{}'
        user = 'postgres'
        password = 'postgres'
        host = 'localhost'
        port = '5432'
        db = 'bookstore'
        url = url.format(user, password, host, port, db)
        engine = create_engine(url, client_encoding='utf8')
        # engine = create_engine(Conf.get_sql_conf('local'))
        #engine = create_engine(Conf.get_sql_conf('local'))
        Base = declarative_base()
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        print("数据库连接成功")
        return self.session