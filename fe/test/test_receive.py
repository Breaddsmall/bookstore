from time import sleep

import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid


class TestReceive:
    seller_id: str
    store_id: str
    buyer_id: str
    password:str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_receive_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_receive_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_receive_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller=gen_book.seller
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        yield

    def test_ok(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.seller_id,self.order_id)
        assert code == 200
        code = self.buyer.receive(self.order_id)
        assert code == 200
        self.buyer.user_id = self.seller_id
        code, result = self.seller.check_s_balance(self.seller_id, self.store_id)
        assert code == 200
        assert result == 0

        code, result = self.buyer.check_balance()
        assert code == 200
        assert result == self.total_price


    def test_authorization_error(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.seller_id, self.order_id)
        assert code == 200

        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.receive(self.order_id)
        assert code != 200

    # 重复收货（即已收货订单）和状态为已取消、未付款、未发货的订单
    # 对于收货来说是一样的，故一次测试即可。
    def test_repeat_receive(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.receive(self.order_id)
        assert code == 200

        code = self.buyer.receive(self.order_id)
        assert code != 200


    def test_auto_receive(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.seller_id, self.order_id)
        assert code == 200
        sleep(5)
        code = self.buyer.receive(self.order_id)
        assert code != 200

        code, result = self.seller.check_s_balance(self.seller_id,self.store_id)
        assert code == 200
        assert result == 0

        self.buyer.user_id=self.seller_id
        code, result = self.buyer.check_balance()
        assert code == 200
        assert result == self.total_price

