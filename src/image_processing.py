"""画像の鮮明化を行うモジュール.

@author: kawanoichi
"""
import cv2
import numpy as np
import os

class ImageProcessing:
    """画像処理を行うクラス.
    ・画像のリサイズ(resize_img)
    ・画像の鮮明化(sharpening)
    """
    @staticmethod
    def resize_img(img_path, save_path=None, resize_w=100, resize_h=100) -> None:
        """一枚の画像をリサイズ.

        Args:
            img_path (string): リサイズする画像のパス
            save_path (string): リサイズした画像を保存するパス
            resize_w (int): リサイズする画像の幅
            resize_h (int): リサイズする画像の高さ
        """
        try:
            # 読み込み
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            
            if img is None:
                raise FileNotFoundError(f"'{img_path}' is not found")
            
            # リサイズ
            resized_img = cv2.resize(img, (resize_w, resize_h))

            if save_path is not None:
                directory, _ = os.path.split(save_path)
                if directory != "" and not os.path.exists(directory):
                    os.makedirs(directory)
                # 出力画像を保存
                cv2.imwrite(save_path, resized_img)

        except FileNotFoundError as e:
            print("Error:", e)
            exit(1)


    @staticmethod
    def sharpening(img_path: str, save_path=None) -> np.ndarray:
        """画像の鮮明化を行う関数.
        手法：カラー画像のアンシャープマスク

        Args:
            image_path(str):鮮明化する画像パス 
            save_path(str):鮮明化した画像の保存先パス
        Return:
            result(numpy.ndarray): 鮮明化後画像
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
            if save_path is not None:
                directory, _ = os.path.split(save_path)
                if directory != "" and not os.path.exists(directory):
                    os.makedirs(directory)
                # 出力画像を保存
                cv2.imwrite(save_path, result)
            return result
        
        except FileNotFoundError as e:
            print("Error:", e)
            exit(1)