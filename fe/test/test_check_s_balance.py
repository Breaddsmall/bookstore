import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid


class TestCheckSBalance:
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
        self.seller_id = "test_check_s_balance_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_check_s_balance_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_check_s_balance_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller
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

    # 检查金额是否正确
    def test_ok(self):
        code, s_balance = self.seller.check_s_balance(self.seller_id, self.store_id)
        assert code == 200
        assert s_balance == 0
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code,s_balance = self.seller.check_s_balance(self.seller_id,self.store_id)
        assert code == 200
        assert s_balance == self.total_price
        code = self.seller.ship(self.seller_id,self.order_id)
        assert code == 200
        code = self.buyer.receive(self.order_id)
        assert code == 200
        code, s_balance = self.seller.check_s_balance(self.seller_id, self.store_id)
        assert code == 200
        assert s_balance == 0

    def test_authorization_error(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.seller.check_s_balance(self.seller_id,self.store_id)
        assert code != 200

    # 两种情况：存在的用户和商店，但商店不是用户的（没有权限）；不存在的商店
    def test_non_exist_store_error(self):
        code = self.seller.check_s_balance(self.buyer_id,self.store_id)
        assert code != 200
        self.store_id = self.store_id + "_x"
        code = self.seller.check_s_balance(self.seller_id,self.store_id)
        assert code != 200
