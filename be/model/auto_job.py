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
        self.conn.commit()
        exit(0)




def execute_job(order_id, mode):
    thread = myThread("ID" + order_id, "name" + order_id, order_id, mode)
    thread.start()

