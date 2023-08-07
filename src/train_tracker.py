"""列車捕捉モジュール.

列車を捕捉する
@author: desty505 miyashita64
"""

import cv2
import numpy as np
from camera_interface import CameraInterface


class TrainTracker:
    """列車を捕捉するクラス."""

    def __init__(self, camera_id: int) -> None:
        """コンストラクタ.

        Args:
            camera_id (int): カメラID
        """
        self.camera = CameraInterface(camera_id)
        self.diff_border = 20       # 動体検知におけるフレームの差の閾値
        self.observe_rect_points = [(0, 0), (0, 0)]

    def calibrate(self) -> None:
        """キャリブレーション."""
        # 録画を開始する
        video, mark_video = self.camera.start_record()
        # クリックに対するコールバックを設定
        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", self.mouse_callback)

        while True:
            # フレームを取得
            success, frame = self.camera.get_frame()
            if not success:
                break

            # クリックされた領域の描画
            mark_frame = self.draw_observe_rect(frame)

            # フレームの表示
            cv2.imshow("Calibration", mark_frame)
            # フレームのファイル出力
            video.write(frame)              # 撮影した動画
            mark_video.write(mark_frame)    # 輪郭線を描画した動画

            # "q"キーを押すとループを抜けて終了
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # リソースを解放
        self.camera.end_record()

    def mouse_callback(self, event, x, y, flags, param) -> None:
        """キャリブレーションのクリック時の処理.

        Args:
            event: クリックイベント
            x: クリックのx座標
            y: クリックのy座標
            flags: 追加情報のフラグ
            param: 任意パラメータ
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # クリック時の座標を記録(最新の2点のみ保持)
            self.observe_rect_points = [self.observe_rect_points[-1], (x, y)]

    def draw_observe_rect(self, frame) -> np.ndarray:
        """監視する領域をフレームに描画する.

        Args:
            frame: 描画対象フレーム
        Returns:
            mark_frame: 監視する領域を描画したフレーム
        """
        mark_frame = frame.copy()
        cv2.rectangle(mark_frame, self.observe_rect_points[-1],
                      self.observe_rect_points[-2], (0, 255, 255), 2)
        return mark_frame

    def observe(self) -> None:
        """映像を監視する."""
        # 録画を開始する
        video, mark_video = self.camera.start_record()

        initial_frame = None
        # フレームを取得して動画に書き込む
        while True:
            # フレームを取得
            success, frame = self.camera.get_frame()
            if not success:
                break

            # 初期フレームを保持
            if initial_frame is None:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                initial_frame = gray_frame.copy().astype("float")
                # 以降の処理をスキップし次のループへ
                continue
            # 動体の検出
            mark_frame = self.detect_motion(frame, initial_frame)
            # 列車の検出
            mark_frame, train_rect_points = self.detect_train(mark_frame)
            # クリックされた領域の描画
            mark_frame = self.draw_observe_rect(mark_frame)

            if len(train_rect_points) >= 2:
                # 列車の境界
                (train_left, train_top), (train_right,
                                          train_bottom) = train_rect_points
                # 描画した指定領域
                observe_y_values = [
                    y for x, y in self.observe_rect_points[-2:]]
                observe_x_values = [
                    x for x, y in self.observe_rect_points[-2:]]

                observe_top = min(observe_y_values)
                observe_bottom = max(observe_y_values)
                observe_left = min(observe_x_values)
                observe_right = max(observe_x_values)

                # 列車が指定領域に侵入しているかを判定する.
                # 列車の先頭(下方向)のy座標が指定領域内
                if observe_top < train_bottom < observe_bottom:
                    # 列車の動画内の横幅が指定領域内
                    if observe_left < train_left \
                            and train_right < observe_right:
                        # 列車の領域を赤く塗りつぶし
                        cv2.rectangle(mark_frame, train_rect_points[0],
                                      train_rect_points[1], (0, 0, 255), -1)

            # フレームの表示
            cv2.imshow("Frame", mark_frame)
            # フレームのファイル出力
            video.write(frame)              # 撮影した動画
            mark_video.write(mark_frame)    # 輪郭線を描画した動画

            # "q"キーでループを終了
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # リソースを解放
        self.camera.end_record()

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
        thresh = cv2.threshold(delta, self.diff_border,
                               255, cv2.THRESH_BINARY)[1]
        # 輪郭線の検出
        contours, _ = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 輪郭線の描画(描画対象, 輪郭線リスト, 輪郭線のインデックス, 線のRGB値, 線の太さ)
        mark_frame = cv2.drawContours(
            frame.copy(), contours, -1, (0, 255, 0), 3)

        return mark_frame

    def detect_train(self, mark_frame) -> (
            np.ndarray, list[tuple[int, int], tuple[int, int]]):
        """フレームから列車を検出する.

        Args:
            mark_frame (np.ndarray): 現在のフレーム
        Returns:
            mark_frame: 列車の範囲を描画したフレーム
            train_rect_points: 列車の左上座標と右下座標のリスト
        """
        # [0, 255, 0]であるピクセル(緑)を255,そうでないピクセルを0に変換
        green_mask = cv2.inRange(mark_frame, np.array(
            [0, 255, 0]), np.array([0, 255, 0]))

        # 緑色の点を物体として認識するために輪郭検出を行う
        contours, _ = cv2.findContours(
            green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
            # 左上座標(x, y)と右下座標(x+w, y+h)を追加
            train_positions.append((x, y, x + w, y + h))

        # すべての緑色の点の中心座標を計算して赤い枠を描画
        train_rect_points = []
        if len(train_positions) > 0:
            min_x = min(pos[0] for pos in train_positions)
            max_x = max(pos[2] for pos in train_positions)
            min_y = min(pos[1] for pos in train_positions)
            max_y = max(pos[3] for pos in train_positions)
            train_rect_points = [(min_x, min_y), (max_x, max_y)]

            # 物体を赤色の四角形で囲む
            cv2.rectangle(mark_frame, train_rect_points[0],
                          train_rect_points[1], (0, 0, 255), 2)

        return mark_frame, train_rect_points
