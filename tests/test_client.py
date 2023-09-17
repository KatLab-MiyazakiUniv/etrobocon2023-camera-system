"""Clientクラスのテストコードを記述するモジュール.

@author: kawanoichi aridome222
"""
from src.client import Client


class TestClient:
    def test_get_robot_state(self):
        # localhostにより処理時間を削減
        client = Client("127.0.0.1")
        # URLの間違いなどによるエラー時のreturnで終了
        client.get_robot_state()

    def test_set_true_camera_action_skip(self):
        # localhostにより処理時間を削減
        client = Client("127.0.0.1")
        # URLの間違いなどによるエラー時のreturnで終了
        client.set_true_camera_action_skip()
