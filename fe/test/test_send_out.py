import time

import pytest

from fe.access import auth,seller
from fe import conf

class TestSendout:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_register_user_{}".format(time.time())
        self.password = "test_register_password_{}".format(time.time())
        self.payment=""
        self.auth = auth.Auth(conf.URL)
        self.seller=seller.Seller(conf.URL)
        yield

    def test_send_out_ok(self):
        code = self.auth.register(self.user_id, self.password)
        assert code == 200
