"""カメラシステムモジュール.

カメラシステムにおいて、一番最初に呼ばれるクラスを定義している
@author: kawanoichi aridome222 miyashita64
"""
import time

from client import Client
from train_tracker import TrainTracker
from robo_snap import RoboSnap


class CameraSystem:
    """カメラシステムクラス."""

    def __init__(self, raspike_ip="192.168.11.17") -> None:
        """カメラシステムのコンストラクタ."""
        self.raspike_ip = raspike_ip

    def start(self) -> None:
        """ゲーム攻略を計画する."""
        print("camera-system start!!")
        # キャリブレーション後に走行体状態取得モジュールを実行する
        # sever_ipは、走行体１なら192.168.11.16、走行体２なら192.168.11.17
        server_ip = self.raspike_ip + ":8000"
        client = Client(server_ip)
        while True:
            state = client.get_robot_state()
            # 走行体の状態が"finish"になった時、終了する。
            if state == "finish":
                print(state)
                break
            elif state == "lap":
                tt = TrainTracker(0)
                # Webカメラのキャリブレーション
                tt.calibrate()
                # IoT列車の監視を開始
                tt.observe()
            else:
                print(state)
            # 2秒待つ
            time.sleep(2)

        # ロボコンスナップ攻略開始
        snap = RoboSnap(self.raspike_ip)
        snap.start_snap()
