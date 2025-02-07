import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid


class TestSearchAllOrderBuyer:
    seller_id: str
    store_id: str
    buyer_id: str
    password:str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_search_all_order_buyer_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_all_order_buyer_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_search_all_order_buyer_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        self.seller = gen_book.seller
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

    def test_authorization_error(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.search_all_order_buyer()
        assert code != 200
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.search_all_order_buyer()
        assert code != 200

    def test_condition_paid(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code,count = self.buyer.search_all_order_buyer()
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="unpaid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="paid")
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="shipped")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="received")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="cancelled")
        assert code == 200
        assert count == 0

    def test_condition_unpaid(self):

        code,count = self.buyer.search_all_order_buyer()
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="unpaid")
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="paid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="shipped")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="received")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="cancelled")
        assert code == 200
        assert count == 0

    def test_condition_shipped(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.seller_id,self.order_id)
        assert code == 200

        code,count = self.buyer.search_all_order_buyer()
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="unpaid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="paid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="shipped")
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="received")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="cancelled")
        assert code == 200
        assert count == 0

    def test_condition_received(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.ship(self.seller_id,self.order_id)
        assert code == 200
        code = self.buyer.receive(self.order_id)

        code,count = self.buyer.search_all_order_buyer()
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="unpaid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="paid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="shipped")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="received")
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="cancelled")
        assert code == 200
        assert count == 0

    def test_condition_cancelled(self):
        code =self.buyer.cancel_order(self.order_id)
        assert code == 200

        code,count = self.buyer.search_all_order_buyer()
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(condition="unpaid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="paid")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="shipped")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="received")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(condition="cancelled")
        assert code == 200
        assert count == 1


    def test_store(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code, count = self.buyer.search_all_order_buyer()
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(store_id=self.store_id)
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(store_id=self.store_id+"_x")
        assert code == 200
        assert count == 0
        code, count = self.buyer.search_all_order_buyer(store_id=self.store_id,condition="paid")
        assert code == 200
        assert count == 1
        code, count = self.buyer.search_all_order_buyer(store_id=self.store_id, condition="unpaid")
        assert code == 200
        assert count == 0





