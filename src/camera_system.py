"""カメラシステムモジュール.

カメラシステムにおいて、一番最初に呼ばれるクラスを定義している
@author: kawanoichi aridome222 miyashita64
"""
import os
import time
import shutil
from datetime import datetime

from client import Client
from train_tracker import TrainTracker
from robo_snap import RoboSnap

script_dir = os.path.dirname(os.path.abspath(__file__))  # noqa
PROJECT_DIR_PATH = os.path.dirname(script_dir)


class CameraSystem:
    """カメラシステムクラス."""

    def __init__(self, raspike_ip="172.20.1.1") -> None:
        """カメラシステムのコンストラクタ."""
        self.raspike_ip = raspike_ip

    @staticmethod
    def mkdir_fig_img() -> None:
        """フィグ画像を格納するディレクトリの作成.

        NOTE:すでにfig_imageが存在する場合はbackup_fig_imageに移動させる
        """
        img_dir_path = os.path.join(PROJECT_DIR_PATH, "fig_image")
        backup_dir = os.path.join(PROJECT_DIR_PATH, "backup_fig_image")

        if os.path.exists(img_dir_path):
            now_time = str(datetime.now())
            now_time = now_time.replace(" ", "_")
            now_time = now_time.replace(":", "-")

            if not os.path.exists(backup_dir):
                os.mkdir(backup_dir)

            source = img_dir_path
            destination = os.path.join(backup_dir, now_time[5:19])
            shutil.copytree(source, destination)

            shutil.rmtree(img_dir_path)
        os.mkdir(img_dir_path)

    def start(self) -> None:
        """ゲーム攻略を計画する."""
        print("camera-system start!!")

        self.mkdir_fig_img()

        # キャリブレーション後に走行体状態取得モジュールを実行する
        # sever_ipは、Bluetooth接続なら172.20.1.1
        # Wi-Fi接続なら、走行体１は192.168.11.16、走行体２は192.168.11.17
        client = Client(self.raspike_ip)
        pre_state = ""

        # Webカメラのキャリブレーション
        tt = TrainTracker(0)
        tt.calibrate()

        while True:
            state = client.get_robot_state()
            # 走行体の状態が"finish"になった時、終了する。
            if state == "finish":
                print(state)
                break
            elif state == "lap" and state != pre_state:
                # IoT列車の監視を開始
                # TODO:observeが"q"を押さないと終了しないバグを修正
                tt.observe()

                # ロボコンスナップ攻略開始
                snap = RoboSnap(self.raspike_ip)
                snap.start_snap()
            else:
                print(state)

            # 状態の保持
            pre_state = state
            # 2秒待つ
            time.sleep(2)
