"""競技システムインタフェース.

競技システムとの通信を行うクラス.
@author: miyashita64
"""
import requests


class OfficialInterface:
    """IoT列車の操作を行うクラス."""

    SERVER_IP = "192.168.100.1"    # 競技システムのIPアドレス
    TEAM_ID = 63                   # チームID

    @classmethod
    def set_train_pwm(cls, pwm) -> bool:
        """IoT列車のPWM値を設定する.

        Args:
            pwm (int): モータ出力

        Returns:
            success (bool): 通信が成功したか(成功:true/失敗:false)
        """
        url = f"http://{cls.SERVER_IP}/train"
        data = {
            "pwm": pwm
        }

        # APIにリクエストを送信
        response = requests.put(url, data=data)
        # レスポンスのステータスコードが200の場合、通信成功
        success = (response.status_code == 200)
        return success

    @classmethod
    def uplode_snap(cls, img_path) -> bool:
        """フィグ画像をアップロードする.

        Args:
            img_path (str): アップロードする画像のパス

        Returns:
            success (bool): 通信が成功したか(成功:true/失敗:false)
        """
        url = f"http://{cls.SERVER_IP}/snap"
        headers = {
            "Content-Type": "image/png"
        }

        # 指定された画像をリクエストに含める
        with open(img_path, "rb") as image_file:
            image_data = image_file.read()
        # チームIDをリクエストに含める
        params = {
            "id": cls.TEAM_ID
        }

        # APIにリクエストを送信
        response = requests.post(url, headers=headers,
                                 data=image_data, params=params)
        # レスポンスのステータスコードが200の場合、通信成功
        success = (response.status_code == 200)
        return success
