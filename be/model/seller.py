import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
import sqlalchemy
from flask import jsonify
import sqlalchemy

class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            self.conn.execute("INSERT into store(store_id, book_id, book_info, stock_level)VALUES ('%s', '%s', '%s', %d)"%(store_id, book_id, book_json_str, stock_level))
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute("UPDATE store SET stock_level = stock_level +%d WHERE store_id = '%s' AND book_id = '%s'"%(add_stock_level, store_id, book_id))
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
            self.conn.execute("INSERT into user_store(user_id, store_id)VALUES('%s','%s')"%(user_id, store_id))
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"
    def send_out(self,seller_id,order_id):
        try:
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)
            self.conn.execute("UPDATE new_order_detail set statue =2 WHERE order_id = ?",(order_id,))
            print("物品已发货")
        except sqlalchemy.exc.IntegrityError as e:
            return 528,"{}".format(str(e))
        return 200,"ok"

