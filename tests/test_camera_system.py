"""CameraSystemクラスのpytestコードを記述するモジュール.

@author: kawanoichi aridome222
@note: モック化はunittestのmockを使用する
"""
from src.camera_system import CameraSystem
from unittest import mock


class TestCameraSystem:
    @mock.patch("src.camera_system.CameraSystem.mkdir_fig_img")
    @mock.patch("src.camera_system.TrainTracker.observe")
    @mock.patch("src.camera_system.TrainTracker.calibrate")
    @mock.patch("src.camera_system.Client.get_robot_state")
    @mock.patch("src.camera_system.RoboSnap.start_snap")
    def test_start(self,
                   mock_upload_snap,
                   mock_get_robot_state,
                   mock_calibrate,
                   mock_observe,
                   mock_mkdir_fig_img
                   ):
        # 引数は、mock.patchが一番下のものから第1引数に対応するため注意
        cs = CameraSystem()

        # モック化したクラスや関数などの返り値を設定
        mock_upload_snap.return_value = None
        mock_get_robot_state.return_value = "lap"
        mock_calibrate.return_value = None
        mock_observe.return_value = None
        mock_mkdir_fig_img.return_value = None

        cs.start()
