from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, \
    Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
import jieba
import psycopg2
from datetime import datetime, time

url = 'postgresql://{}:{}@{}:{}/{}'
user = 'postgres'
password = 'zxcvbnm'
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
    session.execute(
        "CREATE TABLE IF NOT EXISTS book_split ("
        "id int4 PRIMARY KEY, book_intro text); "
    )
    # 提交即保存到数据库
    session.commit()
    # 关闭session
    session.close()


def split():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)
    row = session.execute("SELECT id, book_intro FROM book;").fetchall()
    for i in row:
        tmp = i.book_intro
        ans = ""
        if tmp != None:
            seg_list = jieba.cut_for_search(tmp)
            ans = " ".join(seg_list)
        session.execute(
            "INSERT into book_split(id, book_intro) VALUES (%d, '%s')"
            % (int(i.id), ans))
    session.commit()

    # 关闭session
    session.close()


def add_fts():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)

    session.execute("DROP INDEX IF EXISTS fts_gin_index;")
    session.execute("ALTER TABLE book_split ADD COLUMN fts tsvector;")
    session.execute("UPDATE book_split SET fts = setweight(to_tsvector('english', book_intro), 'A') ;")
    session.execute("CREATE INDEX fts_gin_index ON book_split USING gin (fts);")
    session.commit()

    # 关闭session
    session.close()


if __name__ == "__main__":
    # 创建数据库
    init()
    # 分词
    split()
    # 建索引
    add_fts()
