from time import sleep

from be.model import db_conn
from be.model import error
import sqlalchemy
import threading


class myThread(threading.Thread):
    def __init__(self, threadID, name, order_id, mode):
        threading.Thread.__init__(self)

        self.threadID = threadID
        self.name:str = name
        self.order_id:str = order_id
        self.mode = mode

    def run(self):
        #print("开始线程：" + self.name)
        A=Auto_job()
        sleep(3)
        if self.mode==0:
            A.auto_cancel(self.order_id)
        else:
            A.auto_receive(self.order_id)
        #print("退出线程：" + self.name)



class Auto_job(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def auto_cancel(self, order_id: str):
        self.conn.execute("UPDATE new_order SET condition = 'cancelled' "
                          "WHERE order_id = '%s' AND condition = 'unpaid';" % (order_id))
        self.conn.commit()
        exit(0)

    def auto_receive(self, order_id: str) -> (int, str):
        self.conn.execute("UPDATE new_order SET condition = 'received' "
                          "WHERE order_id = '%s' AND condition = 'shipped';" % (order_id))
        cursor = self.conn.execute(
            "SELECT store_id,total_price FROM new_order "
            "WHERE order_id = '%s';" % (order_id)
        )
        row = cursor.fetchone()
        if row is None:
            return error.error_invalid_order_id(order_id)
        store_id=row[0]
        total_price=row[1]
        cursor = self.conn.execute(
            "SELECT user_id FROM user_store "
            "WHERE store_id = '%s';" % (store_id)
        )
        row = cursor.fetchone()
        if row is None:
            return error.error_non_exist_store_id(store_id)
        seller_id=row[0]
        count = self.conn.execute("UPDATE user_store SET s_balance = s_balance - %d "
                                  "WHERE store_id = '%s' AND s_balance >= %d;"
                                  % (total_price, store_id, total_price))
        if count == 0:
            return error.error_not_sufficient_funds(order_id)  # 卖家余额出错
        # print("checkpoint5")

        count = self.conn.execute("UPDATE usr SET balance = balance+ %d "
                                  "WHERE user_id = '%s';" % (total_price, seller_id))
        # print("checkpoint6")
        if count == 0:
            return error.error_non_exist_user_id(seller_id)
        self.conn.commit()
        exit(0)




def execute_job(order_id, mode):
    thread = myThread("ID" + order_id, "name" + order_id, order_id, mode)
    thread.start()

