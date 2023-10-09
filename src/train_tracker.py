"""列車捕捉モジュール.

列車を捕捉する
@author: desty505 miyashita64
"""

import cv2
import numpy as np
from camera_interface import CameraInterface
from official_interface import OfficialInterface


class TrainTracker:
    """列車を捕捉するクラス."""

    def __init__(self) -> None:
        """コンストラクタ."""
        self.diff_border = 20       # 動体検知におけるフレームの差の閾値
        self.camera = None
        self.observe_rect_points = [(0, 0), (0, 0)]

    def calibrate(self) -> None:
        """キャリブレーション."""
        WINDOW_NAME = "Calibration"
        self.camera = None
        self.observe_rect_points = [(0, 0), (0, 0)]
        while True:
            # キャリブレーション用のウィンドウを生成
            cv2.namedWindow(WINDOW_NAME)
            # クリックに対するコールバックを設定
            cv2.setMouseCallback(WINDOW_NAME, self.mouse_callback)

            # 入力された数字をカメラIDとして扱う
            print("Press key for the camera ID with focus on the Calibration window.")
            key = cv2.waitKey(0)
            # 数字が入力されるまで入力を要求する
            while not chr(key).isdecimal():
                key = cv2.waitKey(0)
            camera_id = int(chr(key))
            # 入力されたカメラIDでCameraInterfaceのインスタンス化を試す
            try:
                camera = CameraInterface(camera_id)
                success, _ = camera.get_frame()
                if not success:
                    raise Exception(f"Error: Unable to access a camera with camera ID {camera_id}.")
            # CameraInterfaceのインスタンス化に失敗した場合、再度カメラIDの入力にもどる
            except Exception as error:
                print(error)
                continue

            # 録画を開始する
            video, mark_video = camera.start_record()
            # クリックされた領域を監視対象とする。"q"キーで決定, "r"キーでカメラID再入力
            print("Click the upper left and lower right of the area to observe and press the 'q' key.")
            print("If switching camera, press the 'r' key.")
            while True:
                # フレームを取得
                success, frame = camera.get_frame()
                if not success:
                    break

                # クリックされた領域の描画
                mark_frame = self.draw_observe_rect(frame)

                # フレームの表示
                cv2.imshow(WINDOW_NAME, mark_frame)
                # フレームのファイル出力
                video.write(frame)              # 撮影した動画
                mark_video.write(mark_frame)    # 輪郭線を描画した動画

                # キー受付(1ms間待機)
                key = cv2.waitKey(1)
                # "q"キーを押すと監視範囲&カメラを決定し操作を終了する
                if key == ord("q"):
                    self.camera = camera
                    break
                # "r"キーを押すと再度カメラIDの入力に戻る
                elif key == ord("r"):
                    break
            # 録画を終了する
            camera.end_record()

            # カメラが決定されている場合、キャリブレーション完了とする
            if self.camera is not None:
                print("\nComplete camera calibration.\n")
                break

    def mouse_callback(self, event, x, y, *_) -> None:
        """キャリブレーションのクリック時の処理.

        Args:
            event: クリックイベント
            x: クリックのx座標
            y: クリックのy座標
            _: 使用しない値(追加情報のフラグ, 任意パラメータ)
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # クリック時の座標を記録(最新の2点のみ保持)
            self.observe_rect_points = [self.observe_rect_points[-1], (x, y)]

    def draw_observe_rect(self, frame) -> np.ndarray:
        """監視する領域をフレームに描画する.

        Args:
            frame (np.ndarray): 描画対象フレーム
        Returns:
            mark_frame (np.ndarray): 監視する領域を描画したフレーム
        """
        mark_frame = frame.copy()
        cv2.rectangle(mark_frame, self.observe_rect_points[-1],
                      self.observe_rect_points[-2], (0, 255, 255), 2)
        return mark_frame

    def observe(self) -> None:
        """映像を監視する."""
        WINDOW_NAME = "Observe"
        # キャリブレーション用のウィンドウを生成
        cv2.namedWindow(WINDOW_NAME)

        # 録画を開始する
        video, mark_video = self.camera.start_record()

        # 初期フレームを記録する
        _, frame = self.camera.get_frame()
        initial_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype("float")

        # 動体を監視する
        while True:
            # フレームを取得
            success, frame = self.camera.get_frame()
            if not success:
                break

            # 列車の検出
            mark_frame, train_rect_points = self.detect_train(frame, initial_frame)
            # クリックされた領域の描画
            mark_frame = self.draw_observe_rect(mark_frame)

            if len(train_rect_points) >= 2:
                # 列車の境界 (左,上(使用しない)),(右,下) 
                (train_left, _), (train_right, train_bottom) = train_rect_points
                # 描画した指定領域
                observe_y_values = [y for _, y in self.observe_rect_points]
                observe_x_values = [x for x, _ in self.observe_rect_points]

                observe_top = min(observe_y_values)
                observe_bottom = max(observe_y_values)
                observe_left = min(observe_x_values)
                observe_right = max(observe_x_values)

                # 列車が指定領域に侵入しているかを判定する
                # 列車の先頭(下方向)のy座標が指定領域内
                if observe_top < train_bottom < observe_bottom:
                    # 列車のx座標が指定領域内
                    if observe_left < train_left \
                            and train_right < observe_right:
                        # 列車の領域を赤く塗りつぶし
                        cv2.rectangle(mark_frame, train_rect_points[0],
                                      train_rect_points[1], (0, 0, 255), -1)
                        # IoT列車を停止する
                        OfficialInterface.set_train_pwm(0)
                        # IoT列車攻略を終了する
                        break

            # フレームの表示
            cv2.imshow(WINDOW_NAME, mark_frame)
            # フレームのファイル出力
            video.write(frame)              # 撮影した動画
            mark_video.write(mark_frame)    # 輪郭線を描画した動画

            # 表示のためのウィンドウの1msスリープ
            cv2.waitKey(1)

        # 録画を終了する
        self.camera.end_record()

    def detect_train(self, frame, initial_frame) -> (
            np.ndarray, list[tuple[int, int], tuple[int, int]]):
        """フレームから列車を検出する.

        Args:
            frame (np.ndarray): 現在のフレーム
        Returns:
            mark_frame (np.ndarray): 列車の範囲を描画したフレーム
            train_rect_points (list[tuple[int, int], tuple[int, int]]):
                列車の左上座標と右下座標のリスト
        """
        # グレースケール変換
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 現在のフレームと移動平均との差を計算
        cv2.accumulateWeighted(gray_frame, initial_frame, 0.6)
        delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(initial_frame))
        # 閾値処理で二値化を行い動体を検出する
        thresh = cv2.threshold(delta, self.diff_border,
                               255, cv2.THRESH_BINARY)[1]
        # 輪郭線の検出
        contours, _ = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 輪郭線の描画(描画対象, 輪郭線リスト, 輪郭線のインデックス, 線のRGB値, 線の太さ)
        mark_frame = cv2.drawContours(
            frame.copy(), contours, -1, (0, 255, 0), 3)

        # 物体の位置情報を格納するリスト
        train_xs = []
        train_ys = []

        # 各輪郭を処理して物体の位置情報を取得
        for contour in contours:
            # バウンディングボックスの左上座標、幅、高さを取得
            x, y, w, h = cv2.boundingRect(contour)

            # 物体の位置情報をリストに追加
            train_xs += [x, x+w]
            train_ys += [y, y+h]

        # すべての緑色の点の中心座標を計算して赤いバウンディングボックスを描画
        train_rect_points = []
        if len(train_xs) > 0 and len(train_ys):
            min_x = min(train_xs)
            max_x = max(train_xs)
            min_y = min(train_ys)
            max_y = max(train_ys)
            train_rect_points = [(min_x, min_y), (max_x, max_y)]

            # 物体を赤色のバウンディングボックスで囲む
            cv2.rectangle(mark_frame, train_rect_points[0],
                          train_rect_points[1], (0, 0, 255), 2)

        return mark_frame, train_rect_points
