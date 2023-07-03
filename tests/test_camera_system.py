import pytest
from src.camera_system import CameraSystem
from src.client import Client


class Test_camera_system:
    def test_start(self, mocker):
        mocker.patch.object(Client, "get_robot_state")

        cs = CameraSystem()
