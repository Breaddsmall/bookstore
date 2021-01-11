import sqlite3 as sqlite
import time

import sqlalchemy
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from flask import jsonify
import threading


class Buyer(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            total_price = 0

            for book_id, count in id_and_count:
                cursor = self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = '%s' AND book_id = '%s';" % (store_id, book_id))
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - %d "
                    "WHERE store_id = '%s' and book_id = '%s' and stock_level >= %d; "
                    % (count, store_id, book_id, count))
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                self.conn.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                    "VALUES('%s', '%s', %d, %d);"
                    % (uid, book_id, count, price))  # 添加状态0，该订单为支付

                total_price += price

            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id,total_price,condition) "
                "VALUES('%s', '%s', '%s',%d,'unpaid');"
                % (uid, store_id, user_id, total_price))
            self.conn.commit()
            order_id = uid
        except sqlalchemy.exc.IntegrityError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            print(e)
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.execute(
                "SELECT order_id, user_id, store_id,total_price,condition FROM new_order WHERE order_id = '%s';" % (
                    order_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            total_price = row[3]
            condition = row[4]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            time1=time.time()
            if condition != "unpaid":
                #print(condition,order_id)
                #print("oh"+str(time.time()))
                return error.error_unpayable_order(order_id)

            cursor = conn.execute("SELECT balance, password FROM usr WHERE user_id = '%s';" % (buyer_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT store_id, user_id FROM user_store WHERE store_id ='%s';" % (store_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute("UPDATE usr set balance = balance - %d "
                                  "WHERE user_id = '%s' AND balance >= %d;"
                                  % (total_price, buyer_id, total_price))

            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute("UPDATE user_store set s_balance = s_balance + %d "
                                  "WHERE store_id = '%s';"
                                  % (total_price, store_id))

            if cursor.rowcount == 0:
                return error.error_non_exist_store_id(store_id)
            cursor = conn.execute("UPDATE new_order set condition = 'paid' WHERE order_id ='%s';" % (order_id))
            #print (order_id)
            #time2=time.time()
            #print(time2-time1)
           #print("good"+str(time2))
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_funds(self, user_id:str, password:str, add_value:int) -> (int, str):
        try:
            cursor = self.conn.execute("SELECT password from usr where user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE usr SET balance = balance + %d WHERE user_id = '%s';" % (add_value, user_id))
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            #print(e)
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive(self, user_id: str, password: str, order_id: str) -> (int, str):

        try:
            cursor = self.conn.execute("SELECT password from usr where user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "SELECT order_id, user_id, store_id,total_price,condition FROM new_order "
                "WHERE order_id = '%s'AND user_id = '%s';" % (order_id,user_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            if row[4]!='shipped':
                return error.error_unreceivable_order(order_id)

            store_id=row[2]
            total_price=row[3]

            self.conn.execute("UPDATE new_order SET condition = 'received' "
                              "WHERE order_id ='%s';" % (order_id))

            cursor=self.conn.execute(
                "SELECT user_id FROM user_store "
                "WHERE store_id = '%s';"%(store_id)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)
            seller_id=row[0]

            self.conn.execute("UPDATE user_store SET s_balance = s_balance - %d "
                              "WHERE store_id = '%s' AND s_balance >= %d;"
                              %(total_price,store_id,total_price))


            cursor = self.conn.execute("UPDATE usr SET balance = balance+ %d "
                              "WHERE user_id = %d;"%(seller_id))
            row=cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(seller_id)
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 查找自己的所有订单
    # def search_orde.r(self,user_id:str):
