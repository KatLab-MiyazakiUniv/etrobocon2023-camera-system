"""列車捕捉モジュール.

列車を捕捉する
@author: desty505 miyashita64
"""

import cv2
import numpy as np
from datetime import datetime
import csv
from camera_interface import CameraInterface

class TrainTracker:
    """列車を捕捉するクラス."""

    def __init__(self, camera_id: int) -> None:
        """コンストラクタ.

        Args:
            camera_id (int): カメラID
        """
        self.camera = CameraInterface(camera_id)
        self.diff_border = 20
        self.output_dir = "video/"
    
    def __del__(self) -> None:
        """デストラクタ."""
        del self.camera

    def observe(self) -> None:
        """映像を監視する."""
        # 動画のコーデック(変換器)
        codec = cv2.VideoWriter_fourcc(*'mp4v')

        now = datetime.now().strftime("%Y%m%d%H%M%S")

        # 動画データを定義(出力ファイル名, コーデック, フレームレート, 解像度)
        video = cv2.VideoWriter(
            f"{self.output_dir}{now}.mp4", codec, 20.0, (640, 480))
        mark_video = cv2.VideoWriter(
            f"{self.output_dir}{now}_mark.mp4", codec, 20.0, (640, 480))
        # 動画ファイルからのキャプチャ
        cap = cv2.VideoCapture("video/test4.avi")

        initial_frame = None
        # フレームを取得して動画に書き込む
        while True:
            # フレームを取得
            # success, frame = self.camera.get_frame()
            success, frame = cap.read()
            if not success:
                break

            # 初期フレームを保持
            if initial_frame is None:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                initial_frame = gray_frame.copy().astype("float")
                # 以降の処理をスキップし次のループへ
                continue
            # 動体を検出する
            mark_frame = self.detect_motion(frame, initial_frame)
            # 列車を検出する
            mark_frame, _ = self.detect_train(mark_frame)

            # 動画の表示
            cv2.imshow('Frame', mark_frame)
            # 動画のファイル出力
            video.write(frame)              # 撮影した動画
            mark_video.write(mark_frame)    # 輪郭線を描画した動画

            # 'q'キーでループを終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # リソースを解放
        video.release()        # 動画ファイルを解放
        mark_video.release()   # 動画ファイルを解放
        cv2.destroyAllWindows()  # ウィンドウを閉じる

    def detect_motion(self, frame, initial_frame) -> np.ndarray:
        """フレームから動体を検出する.

        Args:
            frame (np.ndarray): 現在のフレーム
            initial_frame (np.ndarray): 初期フレーム
        Returns:
            mark_frame (np.ndarray): 動体の輪郭線を描画したフレーム
        """
        # グレースケール変換
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 現在のフレームと移動平均との差を計算
        cv2.accumulateWeighted(gray_frame, initial_frame, 0.6)
        delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(initial_frame))
        # 閾値処理で二値化を行う
        thresh = cv2.threshold(delta, self.diff_border, 255, cv2.THRESH_BINARY)[1]
        # 輪郭線の検出
        contours, _ = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 輪郭線の描画(描画対象, 輪郭線リスト, 輪郭線のインデックス, 線のRGB値, 線の太さ)
        mark_frame = cv2.drawContours(
            frame.copy(), contours, -1, (0, 255, 0), 3)

        return mark_frame

    def detect_train(self, mark_frame) -> (np.ndarray, list[tuple[int, int, int, int]]):
        """フレームから列車を検出する.

        Args:
            mark_frame (np.ndarray): 現在のフレーム
        Returns:
            mark_frame: 列車の範囲を描画したフレーム
            train_positions: 列車の左上座標と右下座標のリスト
        """
        # RGB値が[0, 255, 0]の範囲のピクセルをマスクとして取得
        green_mask = (mark_frame == [0, 255, 0]).all(axis=-1)

        # 緑色の範囲内のピクセルをマスクとして取得
        green_mask = cv2.inRange(mark_frame, np.array([0, 255, 0]), np.array([0, 255, 0]))

        # 緑色の点を物体として認識するために輪郭検出を行う
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 物体の位置情報を格納するリスト
        train_positions = []

        # 各輪郭を処理して物体の位置情報を取得
        for contour in contours:
            # 輪郭の点を取得
            for point in contour:
                x, y = point[0]
                # 緑色の点に対して赤い点を描画
                mark_frame[y, x] = [0, 0, 255]

            # 輪郭の外接矩形を取得
            x, y, w, h = cv2.boundingRect(contour)

            # 物体の位置情報をリストに追加
            train_positions.append((x, y, x + w, y + h))  # 左上座標(x, y)と右下座標(x+w, y+h)を追加

        # すべての緑色の点の中心座標を計算して赤い枠を描画
        if len(train_positions) > 0:
            min_x = min(pos[0] for pos in train_positions)
            max_x = max(pos[2] for pos in train_positions)
            min_y = min(pos[1] for pos in train_positions)
            max_y = max(pos[3] for pos in train_positions)

            # 物体を赤色の四角形で囲む
            cv2.rectangle(mark_frame, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)

        return mark_frame, train_positions

# def main():
#     # 動画ファイルのパス
#     video_path = 'video/train_mark.avi'

#     # CSVファイルの出力パス
#     csv_file = 'red.csv'

#     # 動画ファイルからのキャプチャ
#     cap = cv2.VideoCapture(video_path)

#     # 動画ファイルのコーデック(変換器)
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#     # 動画ファイルのフレームレートと解像度を取得
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#     # 動画ファイルの出力設定
#     out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

#     # CSVファイルにヘッダーを書き込む
#     with open(csv_file, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['frame_number', 'x1', 'y1', 'x2', 'y2'])

#     frame_number = 0

#     while cap.isOpened():
#         # フレームの読み込み
#         ret, frame = cap.read()

#         if not ret:
#             break

#         # 緑色の点と物体の位置情報を取得
#         frame_with_green_points, train_positions = detect_green_train(frame)

#         # CSVファイルに赤い枠の座標データを書き込む
#         with open(csv_file, 'a', newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             for x1, y1, x2, y2 in train_positions:
#                 writer.writerow([frame_number, x1, y1, x2, y2])

#         # 動画ファイルにフレームを書き込む
#         out.write(frame_with_green_points)

#         # フレームを表示
#         cv2.imshow('Frame', frame_with_green_points)

#         # 'q'キーでループを終了
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#         frame_number += 1

#     # リソースを解放
#     cap.release()
#     out.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()
