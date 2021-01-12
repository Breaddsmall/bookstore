import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
import sqlalchemy
from flask import jsonify, json
import sqlalchemy

from be.model.auto_job import execute_job


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            self.conn.execute(
                "INSERT into store(store_id, book_id, book_info, stock_level)VALUES ('%s', '%s', '%s', %d)" % (
                    store_id, book_id, book_json_str, stock_level))
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute(
                "UPDATE store SET stock_level = stock_level +%d WHERE store_id = '%s' AND book_id = '%s'" % (
                    add_stock_level, store_id, book_id))
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.conn.execute(
                "INSERT into user_store(user_id, store_id,s_balance)VALUES('%s','%s',0)" % (user_id, store_id))
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def ship(self, user_id, order_id) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            cursor = self.conn.execute(
                "SELECT store_id,condition FROM new_order WHERE "
                "order_id='%s';" % (order_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            store_id = row[0]
            condition = row[1]

            cursor = self.conn.execute(
                "SELECT user_id FROM user_store WHERE "
                "store_id ='%s' AND user_id='%s';" % (store_id, user_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)
            if condition != "paid":
                return error.error_unshippable_order(order_id)
            self.conn.execute("UPDATE new_order set condition ='shipped' WHERE order_id = '%s';"%(order_id,))
            self.conn.commit()
            execute_job(order_id, 1)
            print("物品已发货")
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def check_s_balance(self, user_id: str, password: str, store_id: str) -> (int, str, int):
        try:
            cursor = self.conn.execute("SELECT password FROM usr WHERE user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "SELECT s_balance FROM user_store WHERE user_id = '%s' AND store_id = '%s';" % (user_id, store_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id), -1
            s_balance = row[0]

        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)), -1
        except BaseException as e:
            return 530, "{}".format(str(e)), -1
        return 200, "ok", s_balance

    def check_stock(self, user_id: str, password: str, store_id: str, book_id: str):
        try:
            cursor = self.conn.execute("SELECT password FROM usr WHERE user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail(), jsonify({})

            if row[0] != password:
                return error.error_authorization_fail(), jsonify({})

            cursor = self.conn.execute(
                "SELECT store_id FROM user_store WHERE user_id = '%s' AND store_id = '%s';" % (user_id, store_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id), jsonify({})

            if book_id != "":
                book_id_p = "AND book_id = '%s'" % (book_id)

            cursor = self.conn.execute(
                "SELECT book_id, stock_level FROM store  WHERE store_id = '%s' %s;" % (
                    store_id, book_id_p))
            book_id_list = []
            stock_level_list = []
            for row in cursor:
                book_id_list.append(row[0])
                stock_level_list.append(row[1])
            msg = jsonify({"book_id": book_id_list, "stock_level": stock_level_list})
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)), jsonify({})
        except BaseException as e:
            return 530, "{}".format(str(e)), jsonify({})
        return 200, "ok", msg
