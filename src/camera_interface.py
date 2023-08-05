"""カメラインターフェースモジュール.

Webカメラの制御を行う
@author: miyashita64
"""

import cv2
import numpy as np

class CameraInterface:
    """カメラを制御するクラス."""

    def __init__(self, camera_id: int) -> None:
        """コンストラクタ.

        Args:
            camera_id (int): カメラID
        """
        self.camera = cv2.VideoCapture(camera_id)

    def __del__(self) -> None:
        """デストラクタ."""
        self.camera.release()  # カメラデバイスを解放

    def get_frame(self) -> (bool, np.ndarray):
        """撮影する.

        Returns:
            success (bool): フレーム取得の可否(true:成功/false:失敗)
            frame (np.ndarray): フレーム
        """
        return self.camera.read()
