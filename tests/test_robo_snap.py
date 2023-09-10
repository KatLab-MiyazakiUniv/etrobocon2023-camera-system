"""ロボコンスナップ攻略クラスのテスト.

@author: miyashita64
"""
from src.robo_snap import RoboSnap
from unittest.mock import Mock, MagicMock, patch
# from requests import Response

RoboSnap
class TestRoboSnap:
    def setup_method(self):
        """前処理."""
        RoboSnap.__IMAGE_LIST = ["FigA_1.png",
                                 "FigA_2.png",
                                 "FigA_3.png",
                                 "FigA_4.png",
                                 "FigB.png"]


        self.raspike_ip = "192.168.11.16"
        self.snap = RoboSnap(self.raspike_ip)

    # モックオブジェクトをテスト対象コードに組み込む
    @patch("self.detect.some_function")
    def test_my_function(self):
        self.snap.start_snap()
