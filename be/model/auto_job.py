from time import sleep

from be.model import db_conn
from be.model import error
import sqlalchemy
import threading


class myThread(threading.Thread):
    def __init__(self, threadID, name, order_id, mode):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.order_id = order_id
        self.job = job[mode]

    def run(self):
        print("开始线程：" + self.name)
        self.job(self.name, self.order_id)
        print("退出线程：" + self.name)


class Auto_job(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def auto_cancel(self, threadName: str, order_id: str):
        sleep(30)
        self.conn.execute("UPDATE new_order SET condition = 'cancelled' "
                          "WHERE order_id = '%s' and condition = 'unpaid';" % (order_id))
        threadName.exit()

    def auto_receive(self, threadName: str, order_id: str) -> (int, str):
        sleep(30)
        self.conn.execute("UPDATE new_order SET condition = 'received' "
                          "WHERE order_id = '%s' and condition = 'shipped';" % (order_id))
        threadName.exit()


job = {
    0: Auto_job.auto_cancel(),
    1: Auto_job.auto_receive()
}


def execute_job(order_id, mode):
    thread = myThread("ID" + order_id, "name" + order_id, order_id, mode)
    thread.start()
    thread.join()
