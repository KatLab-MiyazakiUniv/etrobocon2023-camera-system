"""Clientクラスのテストコードを記述するモジュール.

@author: kawanoichi aridome222
"""
from src.client import Client


class TestClient:
    def test_get_robot_state(self):
        client = Client("127.0.0.1")
        # URLの間違いなどによるエラー時のreturnで終了
        client.get_robot_state()
