"""カメラインターフェースモジュール.

Webカメラの制御を行う
@author: miyashita64 desty505
"""

import cv2
import numpy as np
from datetime import datetime


class CameraInterface:
    """カメラを制御するクラス."""

    def __init__(self, camera_id: int) -> None:
        """コンストラクタ.

        Args:
            camera_id (int): カメラID
        """
        # self.camera = cv2.VideoCapture(camera_id)
        self.camera = cv2.VideoCapture("video/test3.avi")
        self.output_dir = "video/"

    def __del__(self) -> None:
        """デストラクタ."""
        self.camera.release()  # カメラデバイスを解放

    def start_record(self):
        """撮影を開始する.

        Returns:
            video: 撮影した映像
            mark_video: 列車を検出しマークした映像
        """
        # 動画のコーデック(変換器)
        codec = cv2.VideoWriter_fourcc(*'mp4v')

        now = datetime.now().strftime("%Y%m%d%H%M%S")

        # 動画データを定義(出力ファイル名, コーデック, フレームレート, 解像度)
        self.video = cv2.VideoWriter(
            f"{self.output_dir}{now}.mp4", codec, 20.0, (640, 480))
        self.mark_video = cv2.VideoWriter(
            f"{self.output_dir}{now}_mark.mp4", codec, 20.0, (640, 480))
        return self.video, self.mark_video

    def end_record(self) -> None:
        """撮影を終了する."""
        self.video.release()        # 動画ファイルを解放
        self.mark_video.release()   # 動画ファイルを解放
        cv2.destroyAllWindows()  # ウィンドウを閉じる
        # テスト用
        self.camera.release()
        self.camera = cv2.VideoCapture("video/test3.avi")

    def get_frame(self) -> (bool, np.ndarray):
        """撮影する.

        Returns:
            success (bool): フレーム取得の可否(true:成功/false:失敗)
            frame (np.ndarray): フレーム
        """
        return self.camera.read()
