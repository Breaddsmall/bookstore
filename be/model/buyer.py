import sqlite3 as sqlite
import time

import sqlalchemy
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from flask import jsonify
#from be.model.auto_job import execute_job


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

                total_price += price * count

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

            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id,total_price,condition) "
                "VALUES('%s', '%s', '%s',%d,'unpaid');"
                % (uid, store_id, user_id, total_price))

            self.conn.commit()
            # print("下单成功")
            order_id = uid
            #execute_job(order_id, 0)

        except sqlalchemy.exc.IntegrityError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            print(e)
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):

        try:
            cursor = self.conn.execute(
                "SELECT user_id, store_id,total_price,condition FROM new_order WHERE order_id = '%s';" % (
                    order_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            buyer_id = row[0]
            store_id = row[1]
            total_price = row[2]
            condition = row[3]
            # time.sleep(0.5)  # 防止并发导致的查询顺序错误
            #print(condition, order_id)

            if buyer_id != user_id:
                return error.error_authorization_fail()
            # time1=time.time()
            if condition != "unpaid":
                # print(condition,order_id)
                # print("oh"+str(time.time()))
                # print(order_id,condition)
                return error.error_unpayable_order(order_id)

            cursor = self.conn.execute("SELECT balance, password FROM usr WHERE user_id = '%s';" % (buyer_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = self.conn.execute("SELECT store_id, user_id FROM user_store WHERE store_id ='%s';" % (store_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            self.conn.execute("UPDATE usr set balance = balance - %d "
                              "WHERE user_id = '%s' AND balance >= %d;"
                              % (total_price, buyer_id, total_price))

            cursor = self.conn.execute("UPDATE user_store set s_balance = s_balance + %d "
                                       "WHERE store_id = '%s';"
                                       % (total_price, store_id))

            if cursor.rowcount == 0:
                return error.error_non_exist_store_id(store_id)
            cursor = self.conn.execute("UPDATE new_order set condition = 'paid',update_time=CURRENT_TIMESTAMP WHERE order_id ='%s';" % (order_id))
            # print (order_id)
            # time2=time.time()
            # print(time2-time1)
            # print("good"+str(time2))
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.conn.commit()

        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_funds(self, user_id: str, password: str, add_value: int) -> (int, str):
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
            # print(e)
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
            #print("checkpoint1")

            cursor = self.conn.execute(
                "SELECT  store_id,total_price,condition FROM new_order "
                "WHERE order_id = '%s'AND user_id = '%s';" % (order_id, user_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            if row[2] != 'shipped':
                return error.error_unreceivable_order(order_id)
            #print("checkpoint2")

            store_id = row[0]
            total_price = row[1]

            self.conn.execute("UPDATE new_order SET condition = 'received',update_time=CURRENT_TIMESTAMP "
                              "WHERE order_id ='%s';" % (order_id))
            #print("checkpoint3")

            cursor = self.conn.execute(
                "SELECT user_id FROM user_store "
                "WHERE store_id = '%s';" % (store_id)
            )
            #print("checkpoint4")
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = row[0]

            count = self.conn.execute("UPDATE user_store SET s_balance = s_balance - %d "
                                      "WHERE store_id = '%s' AND s_balance >= %d;"
                                      % (total_price, store_id, total_price))
            if count == 0:
                return error.error_not_sufficient_funds(order_id)  # 卖家余额出错
            #print("checkpoint5")

            count = self.conn.execute("UPDATE usr SET balance = balance+ %d "
                                      "WHERE user_id = '%s';" % (total_price, seller_id))
            #print("checkpoint6")
            if count == 0:
                return error.error_non_exist_user_id(seller_id)
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def cancel_order(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.execute("SELECT password FROM usr WHERE user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "SELECT  store_id,total_price,condition FROM new_order "
                "WHERE order_id = '%s'AND user_id = '%s';" % (order_id, user_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            condition = row[2]
            store_id = row[0]
            total_price = row[1]
            if condition == 'received' or condition == 'cancelled':
                return error.error_uncancellable_order(order_id)
            if condition == 'unpaid':
                self.conn.execute("UPDATE new_order SET condition = 'cancelled',update_time=CURRENT_TIMESTAMP "
                                  "WHERE order_id = '%s';" % (order_id))
            elif condition == 'paid' or condition == 'shipped':
                self.conn.execute("UPDATE new_order SET condition = 'cancelled',update_time=CURRENT_TIMESTAMP "
                                  "WHERE order_id = '%s';" % (order_id))
                count = self.conn.execute("UPDATE user_store SET s_balance = s_balance - %d "
                                           "WHERE store_id = '%s' AND s_balance >= %d;"
                                           % (total_price, store_id, total_price))
                if count == 0:
                    return error.error_not_sufficient_funds(order_id)  # 卖家余额出错
                self.conn.execute("UPDATE usr SET balance = balance + %d "
                                  "WHERE user_id = '%s';"
                                  % (total_price, user_id))
            else:
                return error.error_invalid_order_id(order_id)  # 状态出错
            self.conn.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def check_balance(self, user_id: str, password: str) -> (int, str, int):
        try:
            cursor = self.conn.execute("SELECT password,balance from usr where user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id()+(-1)

            if row[0] != password:
                return error.error_authorization_fail()+(-1)
            balance = row[1]
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)), -1
        except BaseException as e:
            return 530, "{}".format(str(e)), -1
        return 200, "ok", balance

    def search_all_order_buyer(self, user_id: str, password: str, store_id: str, condition: str):
        try:
            cursor = self.conn.execute("SELECT password FROM usr WHERE user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()+({"order_id": [], "total_price": [], "store_id": [],"condition_id": [],"count":-1},)

            if row[0] != password:
                return error.error_authorization_fail()+({"count":-1 },)

            store_parameter=""
            condition_parameter=""
            if store_id != "":
                store_parameter = "AND store_id = '%s' " % (store_id)

            if condition != "":
                condition_parameter = " AND condition = '%s' " % (condition)

            cursor = self.conn.execute("SELECT order_id, total_price, store_id, condition FROM new_order "
                                       "WHERE user_id='%s' %s %s;" % (user_id, store_parameter,condition_parameter))
            order_id_list = []
            total_price_list = []
            store_id_list = []
            condition_list = []
            count=0
            for row in cursor:
                order_id_list.append(row[0])
                total_price_list.append(row[1])
                store_id_list.append(row[2])
                condition_list.append(row[3])
                count+=1
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)),{"order_id": [], "total_price": [], "store_id": [],
             "condition_id": [],"count":-1}
        except BaseException as e:
            # print(e)
            return 530, "{}".format(str(e)),{"order_id": [], "total_price": [], "store_id": [],
             "condition_id": [],"count":-1}

        return 200, "ok", {"order_id": order_id_list, "total_price": total_price_list, "store_id": store_id_list,
             "condition_id": condition_list,"count":count}

    def search_order_detail_buyer(self, user_id: str, password: str, order_id: str):
        try:
            cursor = self.conn.execute("SELECT password from usr where user_id='%s';" % (user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()+({"condition":-1,"result_count":-1},)

            if row[0] != password:
                return error.error_authorization_fail()+({"condition":-1,"result_count":-1},)

            cursor = self.conn.execute(
                    "SELECT  store_id,total_price,condition FROM new_order "
                    "WHERE order_id = '%s'AND user_id = '%s';" % (order_id, user_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)+({"condition":-1,"result_count":-1},)

            store_id = row[0]
            total_price = row[1]
            condition = row[2]

            book_id_list = []
            count_list = []
            price_list = []
            result_count=0

            cursor = self.conn.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = '%s';" % (order_id)
            )
            for row in cursor:
                book_id_list.append(row[0])
                count_list.append(row[1])
                price_list.append(row[2])
                result_count+=1

            msg= {"order_id": order_id, "store_id": store_id, "total_price": total_price, "condition": condition,"book_id": book_id_list, "count": count_list, "price": price_list,"result_count":result_count}
        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e)), {"condition":-1,"result_count":-1}
        except BaseException as e:
            return 530, "{}".format(str(e)), {"condition":-1,"result_count":-1}
        return 200, "ok", msg
