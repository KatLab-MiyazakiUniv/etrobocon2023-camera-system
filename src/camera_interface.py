"""カメラインターフェースモジュール.

Webカメラの制御を行う
@author: miyashita64
"""

import cv2
import numpy as np
from datetime import datetime


class CameraInterface:
    """カメラを制御するクラス"""

    def __init__(self, camera_id: int) -> None:
        """コンストラクタ.

        Args:
            camera_id (int): カメラID
        """
        self.camera = cv2.VideoCapture(camera_id)
        self.diff_border = 20
        self.output_dir = "video/"

    def record(self) -> None:
        """動画を撮影する."""
        # 動画のコーデック(変換器)
        codec = cv2.VideoWriter_fourcc(*'XVID')

        now = datetime.now().strftime("%Y%m%d%H%M%S")

        # 動画データを定義(出力ファイル名, コーデック, フレームレート, 解像度)
        video = cv2.VideoWriter(
            f"{self.output_dir}{now}.avi", codec, 20.0, (640, 480))
        mark_video = cv2.VideoWriter(
            f"{self.output_dir}{now}_mark.avi", codec, 20.0, (640, 480))

        initial_frame = None
        # フレームを取得して動画に書き込む
        while True:
            # フレームを取得
            success, frame = self.camera.read()
            if not success:
                break

            # 初期フレームを保持
            if initial_frame is None:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                initial_frame = gray_frame.copy().astype("float")
                # 以降の処理をスキップし次のループへ
                continue
            # 物体検出する
            mark_frame = self.detect_motion(frame, initial_frame)

            # 動画の表示
            cv2.imshow('Frame', mark_frame)
            # 動画のファイル出力
            video.write(frame)              # 撮影した動画
            mark_video.write(mark_frame)    # 輪郭線を描画した動画

            # 'q'キーでループを終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # リソースを解放
        self.camera.release()  # カメラデバイスを解放
        video.release()        # 動画ファイルを解放
        mark_video.release()   # 動画ファイルを解放
        cv2.destroyAllWindows()  # ウィンドウを閉じる

    def detect_motion(self, frame, initial_frame) -> np.ndarray:
        """フレームから動体を検出する.

        Args:
            frame (string): 現在のフレーム
            initial_frame (string): 初期フレーム
        Returns:
            mark_frame: 動体の輪郭線を描画したフレーム
        """

        # グレースケール変換
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 現在のフレームと移動平均との差を計算
        cv2.accumulateWeighted(gray_frame, initial_frame, 0.6)
        delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(initial_frame))
        # 閾値処理で二値化を行う
        thresh = cv2.threshold(
            delta, self.diff_border, 255, cv2.THRESH_BINARY)[1]
        # 輪郭線の検出
        contours, _ = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 輪郭線の検出(描画対象, 輪郭線リスト, 輪郭線のインデックス, 線のRGB値, 線の太さ)
        mark_frame = cv2.drawContours(
            frame.copy(), contours, -1, (0, 255, 0), 3)

        return mark_frame
