from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, \
    Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker

import psycopg2
from datetime import datetime, time

# 连接数据库legend 记得修改这个！！！
# engine = create_engine(Conf.get_sql_conf('local_w'))
url = 'postgresql://{}:{}@{}:{}/{}'
user='postgres'
password='postgres'
host='localhost'
port='5432'
db='bookstore'
url = url.format(user, password, host, port, db)
engine = create_engine(url)
# engine = create_engine(Conf.get_sql_conf('local'))

Base = declarative_base()



def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.execute(
        "CREATE TABLE IF NOT EXISTS usr ("
        "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
        "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS user_store(user_id TEXT, store_id TEXT, PRIMARY KEY(user_id, store_id));"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS store( "
        "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
        " PRIMARY KEY(store_id, book_id))"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS new_order( "
        "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS new_order_detail( "
        "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
        "PRIMARY KEY(order_id, book_id))"
    )

    # 提交即保存到数据库
    session.commit()
    # 关闭session
    session.close()


def add_info():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.execute("INSERT INTO usr values('lh','123456',0,'asdqweq','qweasdasfz')")
    session.commit()
    # 关闭session
    session.close()

if __name__ == "__main__":
    # 创建数据库
    init()
    # 加入信息
    add_info()