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

        # 順番大事
        self.snap.img_list = [
            "black.png",
            "FigA_1.png",
            "FigA_2.png",
            "FigB.png",
            "FigA_3.png",
            "FigA_4.png"]

        self.snap.bash_path = "tests/testdata/test_copy_fig.sh"
        self.snap.img_dir_path = "tests/testdata/img"

    def teardown_method(self):
        """後処理."""
        for img_name in self.snap.img_list:
            path1 = os.path.join(
                self.snap.img_dir_path, "detected_"+img_name)
            path2 = os.path.join(
                self.snap.img_dir_path, "processed_"+img_name)
            delete_img(path1)
            delete_img(path2)

    @mock.patch("src.robo_snap.RoboSnap.set_up")
    @mock.patch("src.robo_snap.DetectObject.detect_object")
    @mock.patch("src.robo_snap.OfficialInterface.upload_snap")
    def test_start_snap(self,
                        mock_upload_snap,
                        mock_detect_object,
                        mock_set_up):
        """ロボコンスナップ攻略クラスのテスト."""
        mock_set_up.return_value = None
        mock_detect_object.return_value = []
        mock_upload_snap.return_value = False
        assert self.snap.start_snap() is None

        # 画像が生成されているかのチェック
        for img in self.snap.img_list:
            check_img_path = os.path.join(
                self.snap.img_dir_path, "processed_"+img)
            assert os.path.exists(check_img_path)

    def test_check_bestshot(self):
        """ロベストショット画像らしさスコアの算出のテスト."""
        # Fig&FrontalFace, ボックス重なってる
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 0.0],
                   [242.0, 131.0, 254.0, 145.0, 0.88, 1.0]]
        assert self.snap.check_bestshot(objects) == 5

        # Fig&FrontalFace, ボックス重なってない
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 0.0],
                   [338.0, 45.0, 353.0, 67.0, 0.88, 1.0]]
        assert self.snap.check_bestshot(objects) == 3

        # Fig&Profile, ボックス重なってる
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 0.0],
                   [242.0, 131.0, 254.0, 145.0, 0.88, 2.0]]
        assert self.snap.check_bestshot(objects) == 4

        # Fig&Profile, ボックス重なってない
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 0.0],
                   [338.0, 45.0, 353.0, 67.0, 0.88, 2.0]]
        assert self.snap.check_bestshot(objects) == 3

        # Fig only
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 0.0]]
        assert self.snap.check_bestshot(objects) == 3

        # FrontalFace only
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 1.0]]
        assert self.snap.check_bestshot(objects) == 2

        # Profile only
        objects = [[226.0, 121.0, 271.0, 196.0, 0.94, 2.0]]
        assert self.snap.check_bestshot(objects) == 1

        # 検出0
        objects = []
        assert self.snap.check_bestshot(objects) == 0
