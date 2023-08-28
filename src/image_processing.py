"""画像の鮮明化を行うモジュール.

@author: kawanoichi
"""
import cv2
import numpy as np
import os


class ImageProcessing:
    """画像処理を行うクラス.

    NOTE:
        以下の関数を保持.
        ・画像のリサイズ(resize_img)
        ・画像の鮮明化(sharpen_image)
    """

    @staticmethod
    def resize_img(img_path,
                   save_path=None,
                   resize_w=640,
                   resize_h=480) -> np.ndarray:
        """一枚の画像をリサイズ.

        Args:
            img_path (str): リサイズする画像のパス
            save_path (str): リサイズした画像を保存するパス
                             パス指定がない場合保存しない
            resize_w (int): リサイズする画像の幅
            resize_h (int): リサイズする画像の高さ

        Return:
            result(numpy.ndarray): リサイズした画像

        Raises:
            FileNotFoundError: 画像が見つからない場合に発生

        """
        try:
            # 読み込み
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

            if img is None:
                raise FileNotFoundError(f"'{img_path}' is not found")

            # リサイズ
            resized_img = cv2.resize(img, (resize_w, resize_h))

            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                # 出力画像を保存
                cv2.imwrite(save_path, resized_img)

            return resized_img

        except FileNotFoundError as e:
            print("Error:", e)

    @staticmethod
    def sharpen_image(img_path: str, save_path=None) -> np.ndarray:
        """画像の鮮明化を行う関数.

        手法：カラー画像のアンシャープマスク

        Args:
            image_path(str): 鮮明化する画像パス
            save_path(str): 鮮明化した画像の保存先パス
                            パス指定がない場合保存しない
        Return:
            result(np.ndarray): 鮮明化後画像

        Raises:
            FileNotFoundError: 画像が見つからない場合に発生
        """
        try:
            # 読み込み
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

            if img is None:
                raise FileNotFoundError(f"'{img_path}' is not found")

            # アンシャープマスクを適用
            blurred = cv2.GaussianBlur(img, (0, 0), 2)  # ぼかし処理
            # 引数: 元画像, 元の画像に対する加重係数（強度）
            #       ブラー画像, ブラー画像に対する減重係数(強度), 画像の明るさ(0は無視)
            result = cv2.addWeighted(img, 2.5, blurred, -1.5, 0)  # 差分から鮮明化
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                # 出力画像を保存
                cv2.imwrite(save_path, result)
            return result

        except FileNotFoundError as e:
            print("Error:", e)


if __name__ == '__main__':
    """作業用."""
    IMAGE_PATH = os.path.join("..", "fig_image")
    image_path = os.path.join(IMAGE_PATH, "test_image.png")
    save_resize_img_path = os.path.join(IMAGE_PATH, "resize_test_image.png")
    save_shaped_img_path = os.path.join(IMAGE_PATH, "shaped_fig.png")

    ImageProcessing.resize_img(image_path, save_resize_img_path)
    ImageProcessing.sharpen_image(image_path, save_shaped_img_path)
    print('完了')
