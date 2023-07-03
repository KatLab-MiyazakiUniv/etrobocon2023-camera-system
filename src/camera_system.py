"""カメラシステムモジュール.

カメラシステムにおいて、一番最初に呼ばれるクラスを定義している
@author: kawanoichi aridome222
"""
from client import Client


class CameraSystem:
    """カメラシステムクラス."""

    def __init__(self) -> None:
        """カメラシステムのコンストラクタ."""
        pass

    def start(self) -> None:
        """ゲーム攻略を計画する."""
        # キャリブレーション後に走行体状態取得モジュールを実行する
        server_ip = "192.168.11.17:8000"  # et2023@katlabなら192.168.11.16、et2023@katlab2なら192.168.11.17
        client = Client(server_ip)
        client.get_robot_state()
