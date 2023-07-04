"""CameraSystemクラスのテストコードを記述するモジュール.

@author: kawanoichi aridome222
"""
from src.camera_system import CameraSystem
from unittest import mock


class TestCameraSystem:
    @mock.patch("src.camera_system.Client.get_robot_state")
    def test_start(self, mock_get_robot_state):
        cs = CameraSystem()
        mock_get_robot_state.return_value = "finish"
        cs.start()
