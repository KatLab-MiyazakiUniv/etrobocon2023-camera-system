"""ロボコンスナップ攻略クラスのテスト.

@author: miyashita64
"""
from src.robo_snap import RoboSnap
from unittest import mock
import os


def delete_img(path):
    """ファイルが存在していたら削除."""
    if os.path.exists(path):
        os.remove(path)


class TestRoboSnap:
    def setup_method(self):
        """前処理."""
        raspike_ip = "192.168.11.16"
        self.snap = RoboSnap(raspike_ip)
        self.snap._RoboSnap__IMAGE_LIST = ["FigA_1.png",
                                           "FigA_2.png",
                                           "FigA_3.png",
                                           "FigA_4.png",
                                           "FigB.png"]
        self.snap._RoboSnap__IMAGE_DIR_PATH = "tests/testdata/img"

    def teardown_method(self):
        """後処理."""
        for img_name in RoboSnap._RoboSnap__IMAGE_LIST:
            path1 = os.path.join(
                self.snap._RoboSnap__IMAGE_DIR_PATH, "detected_"+img_name)
            path2 = os.path.join(
                self.snap._RoboSnap__IMAGE_DIR_PATH, "processed_"+img_name)
            delete_img(path1)
            delete_img(path2)

    @mock.patch("src.robo_snap.OfficialInterface.upload_snap")
    @mock.patch("src.robo_snap.RoboSnap.execute_bash")
    def test_start_snap(self, mock_execute_bash, mock_upload_snap):
        """ロボコンスナップ攻略クラスのテスト."""
        mock_execute_bash.return_value = "execute_bash_result"
        mock_upload_snap.return_value = None
        self.snap.start_snap()
