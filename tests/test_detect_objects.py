"""画像処理クラスのテスト.

@author: kawanoichi
"""
from src.detect_objects import DetectedObject
import os


def delete_img(path):
    """ファイルが存在していたら削除."""
    if os.path.exists(path):
        os.remove(path)


class TestImageProcessing:
    def setup_method(self):
        """前処理."""
        self.img_path = "tests/testdata/img/fig.png"
        self.save_path = "tests/testdata/img/detect_fig.png"
        self.weights = "tests/testdata/yolo/weight.pt"
        self.label_data = "tests/testdata/yolo/label.yaml"
        self.detect = DetectedObject(self.weights, self.label_data)
        delete_img(self.save_path)

    def teardown_method(self):
        """後処理."""
        delete_img(self.save_path)

    def test_detect(self):
        """物体検出のテスト."""
        pred = self.detect.detect_objects(self.img_path, self.save_path)
        assert pred is not False
        det = pred[0]
        assert len(det) == 1
        assert os.path.exists(self.save_path)