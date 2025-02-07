import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid


class TestSearchOrderDetailSeller:
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
        self.seller_id = "test_search_order_detail_seller_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_order_detail_seller_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_search_order_detail_seller_buyer_id_{}".format(str(uuid.uuid1()))
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
        self.seller.password= self.seller.password + "_x"
        code = self.seller.search_order_detail_seller(self.order_id)
        assert code != 200
        self.seller.seller_id = self.seller.seller_id + "_x"
        code = self.seller.search_order_detail_seller(self.order_id)
        assert code != 200

    def test_ok_condition_unpaid(self):
        code, count, condition = self.seller.search_order_detail_seller(self.order_id)
        assert code == 200
        assert condition == "unpaid"

    def test_wrong_buyer(self):
        self.seller.seller_id_id=self.buyer_id
        code = self.seller.search_order_detail_seller(self.order_id)
        assert code != 200

