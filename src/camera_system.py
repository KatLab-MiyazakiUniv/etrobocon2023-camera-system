"""カメラシステムモジュール.

カメラシステムにおいて、一番最初に呼ばれるクラスを定義している
@author: kawanoichi aridome222 miyashita64
"""
import time
from client import Client
from train_tracker import TrainTracker


class CameraSystem:
    """カメラシステムクラス."""

    def __init__(self) -> None:
        """カメラシステムのコンストラクタ."""
        pass

    def start(self) -> None:
        """ゲーム攻略を計画する."""
        print("camera-system start!!")
        # キャリブレーション後に走行体状態取得モジュールを実行する
        # sever_ipは、走行体１なら192.168.11.16、走行体２なら192.168.11.17
        server_ip = "192.168.11.17:8000"
        client = Client(server_ip)
        while True:
            state = client.get_robot_state()
            # 走行体の状態が"finish"になった時、終了する。
            if state == "finish":
                print(state)
                break
            else:
                print(state)
            # 2秒待つ
            time.sleep(2)

        tt = TrainTracker(0)
        tt.calibrate()
        tt.observe()