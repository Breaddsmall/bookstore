import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestCheckBalance:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "check_balance_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        yield


    def test_ok(self):
        code,result = self.buyer.check_balance()
        assert code == 200
        assert result ==0
        code = self.buyer.add_funds(1000)
        assert code == 200
        ode, result = self.buyer.check_balance()
        assert code == 200
        assert result == 1000

    def test_authorization_error(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.check_balance()
        assert code != 200

    def test_non_exist_user_id(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        code, _ = self.buyer.check_balance()
        assert code != 200
