from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, \
    Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker

import psycopg2
from datetime import datetime, time

# 连接数据库legend 记得修改这个！！！
# engine = create_engine(Conf.get_sql_conf('local_w'))
from sqlalchemy_utils import create_database, database_exists

url = 'postgresql://{}:{}@{}:{}/{}'
user = 'postgres'
password = '123456'
host = 'localhost'
port = '5432'
db = 'bookstore'
url = url.format(user, password, host, port, db)
engine = create_engine(url)
# engine = create_engine(Conf.get_sql_conf('local'))

Base = declarative_base()


def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if not database_exists(engine.url):
        create_database(engine.url)


    session.execute(
        "CREATE TABLE IF NOT EXISTS usr ("
        "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
        "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS user_store(user_id TEXT, store_id TEXT,"
        "s_balance INTEGER,"
        " PRIMARY KEY(user_id, store_id));"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS store( "
        "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
        " PRIMARY KEY(store_id, book_id))"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS new_order( "
        "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT,total_price INTEGER,condition TEXT,"
        "update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP);"
    )

    session.execute(
        "CREATE TABLE IF NOT EXISTS new_order_detail( "
        "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER, "
        "PRIMARY KEY(order_id, book_id))"
    )


    # 定义数据库函数（触发器）

    # 以user_id和store_id建立new_order上的索引
    # 原因：除了primary key order_id，还会查询user_id/store_id/condition
    # 其中condition只有五种状态，而user_id和store_id都非常多
    session.execute(
        "CREATE INDEX IF NOT EXISTS search_order_index ON new_order(user_id,store_id)"
    )


    # 提交即保存到数据库
    session.commit()
    # 关闭session
    session.close()

if __name__ == "__main__":
    # 创建数据库
    init()
