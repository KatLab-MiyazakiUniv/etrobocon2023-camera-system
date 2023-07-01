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
        # キャリブレーション後に走行体状況監視モジュールを実行する
        Client.client()
