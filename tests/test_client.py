"""CameraSystemクラスのテストコードを記述するモジュール.

@author: kawanoichi aridome222
"""
from src.client import Client


class TestClient:
    def test_get_robot_state(self):
        client = Client("192.168.11.17:8000")
        client.get_robot_state()
