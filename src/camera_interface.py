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
        # CAP_DSHOWを指定し、Direct Show経由でマルチメディア(映像)を扱う
        # 参考：https://www.klv.co.jp/corner/python-opencv-video-capture.html
        self.camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        self.output_dir = "video/"
        self.video = None
        self.mark_video = None

    def __del__(self) -> None:
        """デストラクタ."""
        self.camera.release()  # カメラデバイスを解放

    def start_record(self) -> (cv2.VideoWriter, cv2.VideoWriter):
        """撮影を開始する.

        Returns:
            video (cv2.VideoWriter): 撮影した映像
            mark_video (cv2.VideoWriter): 列車を検出しマークした映像
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

    def get_frame(self) -> (bool, np.ndarray):
        """撮影する.

        Returns:
            success (bool): フレーム取得の可否(true:成功/false:失敗)
            frame (np.ndarray): フレーム
        """
        success, frame = self.camera.read()
        return (success, frame)
