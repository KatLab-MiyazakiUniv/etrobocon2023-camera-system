"""競技システムインタフェースのテスト.

@author: miyashita64
"""
from src.official_interface import OfficialInterface
from unittest import mock
from requests import Response

class TestOfficialInterface:
    @mock.patch("requests.put")
    def test_set_train_pwm(self, mock_put):
        mock_response = mock.Mock(spec=Response)
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        OfficialInterface.SERVER_IP = "127.0.0.1"   # ローカルホスト
        pwm = 60
        OfficialInterface.set_train_pwm(pwm)

    @mock.patch("requests.post")
    def test_uplode_snap(self, mock_post):
        mock_response = mock.Mock(spec=Response)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        img_path = "tests/testdata/img/fig.png"
        OfficialInterface.uplode_snap(img_path)
