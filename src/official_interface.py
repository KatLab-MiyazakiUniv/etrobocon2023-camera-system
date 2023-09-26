"""競技システムインタフェース.

競技システムとの通信を行うクラス.
@author: miyashita64 kawanoichi
"""
import requests
from image_processing import ImageProcessing
from PIL import Image


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
    def upload_snap(cls, img_path: str) -> bool:
        """フィグ画像をアップロードする.

        Args:
            img_path (str): アップロードする画像のパス

        Returns:
            success (bool): 通信が成功したか(成功:true/失敗:false)
        """
        url = f"http://{cls.SERVER_IP}/snap"
        # リクエストヘッダー
        headers = {
            "Content-Type": "image/png"
        }
        # リクエストパラメータ
        params = {
            "id": cls.TEAM_ID
        }

        try:
            # サイズが正しくない場合はリサイズする
            img = Image.open(img_path)
            width, height = img.size
            if not (width == 640 and height == 480):
                ImageProcessing.resize_img(img_path, img_path, 640, 480)

            # bytes型で読み込み
            with open(img_path, "rb") as image_file:
                image_data = image_file.read()

            # APIにリクエストを送信
            response = requests.post(url, headers=headers,
                                     data=image_data, params=params)
            # レスポンスのステータスコードが201の場合、通信成功
            if response.status_code != 201:
                raise ResponseError("Failed to send fig image.")
            success = True
        except Exception as e:
            print(e)
            success = False
        return success

if __name__ == "__main__":
    print("test-start")
    OfficialInterface.set_train_pwm(10)
    OfficialInterface.upload_snap("../tests/testdata/img/fig.png")
    print("test-end")