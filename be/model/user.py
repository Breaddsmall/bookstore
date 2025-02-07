import jwt
import time
import logging
import sqlite3 as sqlite

from flask import jsonify, json

from be.model import error
from be.model import db_conn
import sqlalchemy
import initialize_db
import base64


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded  # .decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str) -> (int, str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            self.conn.execute(
                "INSERT INTO usr (user_id, password, balance, token, terminal) values ('%s', '%s', 0, '%s', '%s')" % (
                    user_id, password, token, terminal))
            self.conn.commit()
            #print("注册成功",user_id)
        except sqlalchemy.exc.IntegrityError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        cursor = self.conn.execute("SELECT token from usr where user_id='%s'" % (user_id))
        # cursor=self.conn.query(User).filter(User.user_id==user_id).get(token)
        row = cursor.fetchone()
        if row is None:
            print("userid有误")
            return error.error_authorization_fail()
        db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            print("token有误")
            return error.error_authorization_fail()
        print("token正确")
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        cursor = self.conn.execute("SELECT password from usr where user_id='%s'" % (user_id))

        row = cursor.fetchone()
        if row is None:
            print("user_id不存在")
            return error.error_authorization_fail()
        if password != row[0]:
            print("密码不正确")
            return error.error_authorization_fail()
        #print("password正确")
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:

            code, message = self.check_password(user_id, password)

            if code != 200:
                return code, message, ""
            token = jwt_encode(user_id, terminal)
            #print(1)

            cursor = self.conn.execute(
                "UPDATE usr set token= '%s' , terminal = '%s' where user_id = '%s'" % (token, terminal, user_id))
            #print(2)
            if cursor.rowcount == 0:
                return error.error_authorization_fail() + ("",)
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e)), ""
        #print("登录成功")
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> (int, str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            cursor = self.conn.execute(
                "UPDATE usr SET token = '%s', terminal = '%s' WHERE user_id='%s'" % (token, terminal, user_id))
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            cursor = self.conn.execute("DELETE from usr where user_id='%s'" % (user_id,))
            if cursor.rowcount == 1:
                self.conn.commit()
            else:
                return error.error_authorization_fail()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            cursor = self.conn.execute(
                "UPDATE usr set password = '%s', token= '%s' , terminal = '%s' where user_id = '%s'" % (
                    new_password, token, terminal, user_id))
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def search_author(self, author: str) -> (int, [dict]):  # 200,'ok',list[{str,str,str,str,list,bytes}]
        ret = []
        a = '%'
        temp = author
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE author LIKE '%s' " % (
                c)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_book_intro(self, book_intro: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = book_intro
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE book_intro LIKE '%s' " % (
                c)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_tags(self, tags: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = tags
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE tags LIKE '%s' " % (
                c)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_title(self, title: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = title
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE title LIKE '%s' " % (
                c)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_author_in_store(self, author: str, store_id: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = author
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE author LIKE '%s' and book.id in (select book_id::int4 from store where store_id='%s')" % (
                c, store_id)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_book_intro_in_store(self, book_intro: str, store_id: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = book_intro
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE book_intro LIKE '%s' and book.id in (select book_id::int4 from store where store_id='%s') " % (
                c, store_id)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_tags_in_store(self, tags: str, store_id: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = tags
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE tags LIKE '%s' and book.id in (select book_id::int4 from store where store_id='%s')" % (
                c, store_id)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_title_in_store(self, title: str, store_id: str) -> (int, [dict]):
        ret = []
        a = '%'
        temp = title
        b = '%'
        c = a + temp + b
        records = self.conn.execute(
            " SELECT title,author,publisher,book_intro,tags FROM book WHERE title LIKE '%s' and book.id in (select book_id::int4 from store where store_id='%s') " % (
                c, store_id)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_book_intro_index_version(self, book_intro: str) -> (int, [dict]):
        ret = []
        temp = book_intro
        records = self.conn.execute(
            "SELECT book.title,book.author,book.publisher,book.book_intro,book.tags FROM book WHERE book.id in (SELECT id FROM book_split WHERE fts @@ to_tsquery('%s'));" % (
                temp)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []

    def search_book_intro_index_version_in_store(self, book_intro: str, store_id: str) -> (int, [dict]):
        ret = []
        temp = book_intro
        records = self.conn.execute(
            "SELECT book.title,book.author,book.publisher,book.book_intro,book.tags FROM book WHERE book.id in (SELECT id FROM book_split WHERE fts @@ to_tsquery('%s')) and book.id in (select book_id::int4 from store where store_id='%s') ;" % (
                temp, store_id)).fetchall()
        if len(records) != 0:
            for i in range(len(records)):
                record = records[i]
                title = record[0]
                author = record[1]
                publisher = record[2]
                book_intro = record[3]
                tags = record[4]
                ret.append(
                    {'title': title, 'author': author, 'publisher': publisher,
                     'book_intro': book_intro,
                     'tags': tags})
            return 200, ret
        else:
            return 200, []




