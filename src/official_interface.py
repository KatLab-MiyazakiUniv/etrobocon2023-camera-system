"""競技システムインタフェース.

競技システムとの通信を行うクラス.
@author: miyashita64 kawanoichi
"""
import requests
from image_processing import ImageProcessing


class ResponseError(Exception):
    """レスポンスエラー用の例外."""

    def __init__(self, message: str):
        """コンストラクタ.

        Args:
            message (string): エラーメッセージ
        """
        super().__init__(message)


class OfficialInterface:
    """IoT列車の操作を行うクラス."""

    SERVER_IP = "192.168.100.1"    # 競技システムのIPアドレス
    TEAM_ID = 63                   # チームID

    @classmethod
    def set_train_pwm(cls, pwm: int) -> bool:
        """IoT列車のPWM値を設定する.

        Args:
            pwm (int): モータ出力

        Returns:
            success (bool): 通信が成功したか(成功:true/失敗:false)
        """
        url = f"http://{cls.SERVER_IP}/train?pwm={pwm}"
        try:
            # APIにリクエストを送信
            response = requests.put(url)
            # レスポンスのステータスコードが200の場合、通信成功
            if response.status_code != 200:
                raise ResponseError("Failed to set PWM for IoT train.")
            success = True
        except Exception as e:
            print(e)
            success = False
        return success

    @classmethod
    def upload_snap(cls, img_path: str, resize_img_path: str) -> bool:
        """フィグ画像をアップロードする.

        Args:
            img_path (str): アップロードする画像のパス
            resize_img_path (str): リサイズした画像を保存するパス

        Returns:
            success (bool): 通信が成功したか(成功:true/失敗:false)
        """
        url = f"http://{cls.SERVER_IP}/snap"
        # リクエストヘッダー
        headers = {
            "Content-Type": "image/png"
        }

        # 指定された画像をリクエストに含める
        ImageProcessing.resize_img(img_path, resize_img_path, 640, 480)
        with open(resize_img_path, "rb") as image_file:
            image_data = image_file.read()
        # チームIDをリクエストに含める
        params = {
            "id": cls.TEAM_ID
        }

        try:
            # 指定された画像をリサイズする
            cls.resize_img(img_path, resize_img_path)
            with open(resize_img_path, "rb") as resize_image_file:
                image_data = resize_image_file.read()
            # APIにリクエストを送信
            response = requests.post(url, headers=headers,
                                     data=image_data, params=params)
            # レスポンスのステータスコードが200の場合、通信成功
            if response.status_code != 200:
                raise ResponseError("Failed to send fig image.")
            success = True
        except Exception as e:
            print(e)
            success = False
        return success
