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

        # fig_imageディレクトリが存在する場合
        if os.path.exists(img_dir_path):
            # fig_imageの中にファイルが存在する場合
            if len(os.listdir(img_dir_path)):
                now_time = datetime.now().strftime("%m-%d_%Hh%Mm%Ss")
                if not os.path.exists(backup_dir):
                    # backup_fig_image作成
                    os.mkdir(backup_dir)
                # 移動先パス
                backup_path = os.path.join(backup_dir, now_time)
                # 移動
                shutil.move(img_dir_path, backup_path)
            else:
                # fig_image削除
                shutil.rmtree(img_dir_path)
        # fig_image作成
        os.mkdir(img_dir_path)

    def start(self) -> None:
        """ゲーム攻略を計画する."""
        print("camera-system start!!")

        self.mkdir_fig_img()

        # キャリブレーション後に走行体状態取得モジュールを実行する
        # sever_ipは、Bluetooth接続なら172.20.1.1
        # Wi-Fi接続なら、走行体１は192.168.11.16、走行体２は192.168.11.17
        client = Client(self.raspike_ip)

        # Webカメラのキャリブレーション
        tt = TrainTracker()
        tt.calibrate()

        while True:
            # 走行状況を取得
            state = client.get_robot_state()
            if state == "lap":
                # IoT列車の監視を開始
                tt.observe()

                # ロボコンスナップ攻略開始
                snap = RoboSnap(self.raspike_ip)
                snap.start_snap()

                # カメラシステムを終了
                break
            else:
                print(state)

            # 2秒待つ
            time.sleep(2)
