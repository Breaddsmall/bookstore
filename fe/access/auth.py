import requests
from urllib.parse import urljoin
import sqlalchemy


class Auth:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/")

    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")

    def register(
            self,
            user_id: str,
            password: str
    ) -> int:
        json = {
            "user_id": user_id,
            "password": password
        }
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code

    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code

    def logout(self, user_id: str, token: str) -> int:
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def unregister(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code

    def search_author(self, author: str) -> int:
        json = {"author": author}
        url = urljoin(self.url_prefix, "search_author")
        r = requests.post(url, json=json)
        return r.status_code

    def search_book_intro(self, book_intro: str) -> int:
        json = {"book_intro": book_intro}
        url = urljoin(self.url_prefix, "search_book_intro")
        r = requests.post(url, json=json)
        return r.status_code

    def search_tags(self, tags: str) -> int:
        json = {"tags": tags}
        url = urljoin(self.url_prefix, "search_tags")
        r = requests.post(url, json=json)
        return r.status_code

    def search_title(self, title: str) -> int:
        json = {"title": title}
        url = urljoin(self.url_prefix, "search_title")
        r = requests.post(url, json=json)
        return r.status_code

    def search_author_in_store(self, author: str, store_id: str) -> int:
        json = {"author": author, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_author_in_store")
        r = requests.post(url, json=json)
        return r.status_code

    def search_book_intro_in_store(self, book_intro: str, store_id: str) -> int:
        json = {"book_intro": book_intro, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_book_intro_in_store")
        r = requests.post(url, json=json)
        return r.status_code

    def search_tags_in_store(self, tags: str, store_id: str) -> int:
        json = {"tags": tags, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_tags_in_store")
        r = requests.post(url, json=json)
        return r.status_code

    def search_title_in_store(self, title: str, store_id: str) -> int:
        json = {"title": title, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_title_in_store")
        r = requests.post(url, json=json)
        return r.status_code

    def search_book_intro_index_version(self, book_intro: str) -> int:
        json = {"book_intro": book_intro}
        url = urljoin(self.url_prefix, "search_book_intro_index_version")
        r = requests.post(url, json=json)
        return r.status_code

    def search_book_intro_index_version_in_store(self, book_intro: str, store_id: str) -> int:
        json = {"book_intro": book_intro, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_book_intro_in_store")
        r = requests.post(url, json=json)
        return r.status_code

    def search_all_order(self, user_id: str, password: str, store_id: str, condition: str, is_buyer: str):
        json = {"user_id": user_id, "password": password, "store_id": store_id, "condition": condition,
                "is_buyer": is_buyer}
        url = urljoin(self.url_prefix, "search_all_order")
        r = requests.post(url, json=json)
        return r.status_code

    def search_order_detail(self, user_id: str, password: str, order_id: str, is_buyer: str):
        json = {"user_id": user_id, "password": password, "order_id": order_id, "is_buyer": is_buyer}
        url = urljoin(self.url_prefix, "search_order_detail")
        r = requests.post(url, json=json)
        return r.status_code

    def check_balance(self, user_id: str, password: str):
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "check_balance")
        r = requests.post(url, json=json)
        return r.status_code
