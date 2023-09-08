"""画像処理クラスのテスト.

@author: kawanoichi
"""
from src.image_processing import ImageProcessing
import cv2
import os


def delete_img(path):
    """ファイルが存在していたら削除."""
    if os.path.exists(path):
        os.remove(path)


class TestImageProcessing:
    def setup_method(self):
        """前処理."""
        self.img_path = "tests/testdata/img/fig.png"
        self.wrong_path = "wrong.png"
        self.save_resize_img = "tests/testdata/img/resized_fig_2.png"
        self.save_sharpened_img = "tests/testdata/img/sharpened_fig.png"
        delete_img(self.save_resize_img)
        delete_img(self.save_sharpened_img)

    def teardown_method(self):
        """後処理."""
        delete_img(self.save_resize_img)
        delete_img(self.save_sharpened_img)

    def test_sharpen_image(self):
        """鮮明化のテスト."""
        expect_img = cv2.imread(self.img_path)
        sharpened_img = ImageProcessing.sharpen_image(
            self.img_path, self.save_sharpened_img)
        assert sharpened_img.shape == expect_img.shape
        assert os.path.exists(self.save_sharpened_img)

        # パスが間違っている場合
        sharpened_img = ImageProcessing.sharpen_image(
            self.wrong_path, self.save_sharpened_img)
        assert sharpened_img is None

    def test_resize_img(self):
        """リサイズのテスト."""
        resize_img = ImageProcessing.resize_img(
            self.img_path, self.save_resize_img, resize_w=320, resize_h=240)
        assert resize_img.shape == (240, 320, 3)
        assert os.path.exists(self.save_resize_img)

        # パスが間違っている場合
        resize_img = ImageProcessing.resize_img(
            self.wrong_path, self.save_resize_img, resize_w=320, resize_h=240)
        assert resize_img is None
