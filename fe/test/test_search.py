import time
import pytest
from fe.access import auth
from fe import conf
import uuid


class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        self.author = "test_author_{}".format(str(uuid.uuid1()))
        self.book_intro = "test_book_intro_{}".format(str(uuid.uuid1()))
        self.tags = "test_tags_{}".format(str(uuid.uuid1()))
        self.title = "test_title_{}".format(str(uuid.uuid1()))
        self.store_id = "test_store_id_{}".format(str(uuid.uuid1()))
        yield

    # 采用like语句直接查询关键词的搜索方法
    def test_search(self):
        self.store_id = "test_add_books_store_id_e57c7e37-5342-11eb-bdd5-94b86d54714d"
        assert self.auth.search_author("西尔维娅") == 200
        assert self.auth.search_book_intro("三毛流浪") == 200
        assert self.auth.search_tags("传记") == 200
        assert self.auth.search_title("流浪记") == 200
        assert self.auth.search_author_in_store("西尔维娅", self.store_id) == 200
        assert self.auth.search_book_intro_in_store("三毛", self.store_id) == 200
        assert self.auth.search_tags_in_store("传记", self.store_id) == 200
        assert self.auth.search_title_in_store("三毛", self.store_id) == 200

    # 采用PostgreSQL 全文检索功能的改进版搜索方法
    def test_search_index_version(self):
        self.store_id = "test_add_books_store_id_e57c7e37-5342-11eb-bdd5-94b86d54714d"
        assert self.auth.search_book_intro("三毛") == 200
        assert self.auth.search_book_intro_in_store("三毛", self.store_id) == 200
