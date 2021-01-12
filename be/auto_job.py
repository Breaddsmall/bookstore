from be.model import db_conn

def auto_cancel():
    conn=db_conn.DBConn().conn
    conn.execute("UPDATE new_order SET condition = 'cancelled' "
                 "WHERE condition = 'unpaid' AND CURRENT_TIMESTAMP-update_time >= interval '3 SECOND' ;")
    conn.commit()

def auto_receive():
    conn=db_conn.DBConn().conn
    cursor=conn.execute("SELECT order_id,store_id,total_price FROM new_order WHERE condition = 'shipped' AND CURRENT_TIMESTAMP-update_time >= interval '3 SECOND';")
    for row in cursor:
        order_id=row[0]
        store_id=row[1]
        total_price=row[2]
        conn.execute("UPDATE new_order SET condition = 'received' WHERE order_id = '%s';"%(order_id))
        conn.execute("UPDATE user_store SET s_balance = s_balance - %d WHERE store_id ='%s';"%(total_price,store_id))
        c=conn.execute("SELECT user_id FROM user_store WHERE store_id='%s';"%(store_id))
        r=c.fetchone()
        user_id=r[0]
        conn.execute("UPDATE usr SET balance = balance + %d WHERE user_id = '%s';"%(total_price,user_id))
    conn.commit()
