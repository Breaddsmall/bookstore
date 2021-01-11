import logging
import os
import sqlite3 as sqlite

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker
from initialize_db import init
import psycopg2
from sqlalchemy_utils import database_exists, create_database


class Store:
    def __init__(self):
        # 连接数据库legend 记得修改这个！！！
        # engine = create_engine(Conf.get_sql_conf('local_w'))
        url = 'postgresql://{}:{}@{}:{}/{}'
        user = 'postgres'
        password = '123456'
        host = 'localhost'
        port = '5432'
        db = 'bookstore'
        url = url.format(user, password, host, port, db)
        engine = create_engine(url, client_encoding='utf8')
        if not database_exists(engine.url):
            init()
        # engine = create_engine(Conf.get_sql_conf('local'))
        #engine = create_engine(Conf.get_sql_conf('local'))
        Base = declarative_base()
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        print("数据库连接成功")
        return self.session