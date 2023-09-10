"""CameraSystemクラスのpytestコードを記述するモジュール.

@author: kawanoichi aridome222
@note: モック化はunittestのmockを使用する
"""
from src.camera_system import CameraSystem
from unittest import mock


class TestCameraSystem:
    @mock.patch("src.camera_system.TrainTracker.observe")
    @mock.patch("src.camera_system.TrainTracker.calibrate")
    @mock.patch("src.camera_system.Client.get_robot_state")
    @mock.patch("src.camera_system.RoboSnap.start_snap")
    def test_start(self,
                   mock_upload_snap,
                   mock_get_robot_state,
                   mock_calibrate,
                   mock_observe):
        # 引数は、mock.patchが一番下のものから第1引数に対応するため注意
        cs = CameraSystem()
        # finishを返すようにモック化
        mock_get_robot_state.return_value = "finish"
        mock_calibrate.return_value = None
        mock_observe.return_value = None
        mock_upload_snap.return_value = None

        cs.start()
