import requests
from urllib.parse import urljoin
from fe.access import book
from fe.access.auth import Auth


class Seller:
    def __init__(self, url_prefix, seller_id: str, password: str):
        self.url_prefix = urljoin(url_prefix, "seller/")
        self.seller_id = seller_id
        self.password = password
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.seller_id, self.password, self.terminal)
        assert code == 200

    def create_store(self, store_id):
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "create_store")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_book(self, store_id: str, stock_level: int, book_info: book.Book) -> int:
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
            "book_info": book_info.__dict__,
            "stock_level": stock_level
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "add_book")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_stock_level(self, seller_id: str, store_id: str, book_id: str, add_stock_num: int) -> int:
        json = {
            "user_id": seller_id,
            "store_id": store_id,
            "book_id": book_id,
            "add_stock_level": add_stock_num
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "add_stock_level")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def ship(self, seller_id: str, order_id: str):
        json = {
            "user_id": seller_id,
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "ship")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def check_s_balance(self,seller_id, store_id: str):
        json = {
            "user_id": seller_id,
            "password": self.password,
            "store_id": store_id,
        }
        url = urljoin(self.url_prefix, "check_s_balance")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        json = r.json()
        return r.status_code,json["result"]

    def check_stock(self, seller_id: str, password: str, store_id: str, book_id: str) -> int:
        json = {
            "user_id": seller_id,
            "password": password,
            "store_id": store_id,
            "book_id": book_id,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "check_stock")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)

        return r.status_code

    def search_all_order_seller(self, condition: str):
        json = {"user_id": self.user_id, "password": self.password, "store_id": self.store_id, "condition": condition,}
        url = urljoin(self.url_prefix, "search_all_order_seller")
        r = requests.post(url, json=json)
        result = r.json().get("result")
        count = result.json().get("count")
        return r.status_code, count

    def search_order_detail_seller(self, order_id: str):
        json = {"user_id": self.user_id, "password": self.password, "order_id": order_id,}
        url = urljoin(self.url_prefix, "search_order_detail_seller")
        r = requests.post(url, json=json)
        result = r.json().get("result")
        count = result.json().get("result_count")
        condition = result.json().get("condition")
        return r.status_code, count, condition