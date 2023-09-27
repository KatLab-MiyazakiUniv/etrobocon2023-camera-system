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

    def __init__(self, raspike_ip="172.20.1.1") -> None:
        """カメラシステムのコンストラクタ."""
        self.raspike_ip = raspike_ip

    def start(self) -> None:
        """ゲーム攻略を計画する."""
        print("camera-system start!!")
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
