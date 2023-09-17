"""走行体状態取得モジュール.

走行体の状態を取得する.
@author: aridome222 miyashita64
@note: 参考 https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217
"""
import urllib.request


class Client:
    """走行体のサーバにリクエストを送り、ロボットの状態を取得するクラス."""

    def __init__(self, server_ip: str) -> None:
        """Clientのコンストラクタ.

        Args:
            server_ip (string): サーバのIPアドレス
        """
        self.server_ip = server_ip

    def get_robot_state(self) -> str:
        """走行体の状態を取得するために、サーバにリクエストを送る.

        Returns:
            response_text: 走行体の状態
        """
        url = f"http://{self.server_ip}/robot_info/state"
        req = urllib.request.Request(url)
        response_text = ""

        try:
            with urllib.request.urlopen(req) as res:
                response_data = res.read()
                # byte型のデータ"response_data"をstr型の文字列"response_text"にデコードを行う
                charset = 'UTF-8'
                response_text = response_data.decode(charset, 'replace')
        # HTTP通信でのエラー時
        except urllib.error.HTTPError as err:
            print(err.code)
            return
        # URLの間違いなどによるエラー時
        except urllib.error.URLError as err:
            print(err.reason)
            return

        return response_text

    def set_true_camera_action_skip(self) -> bool:
        """撮影終了フラグを立てる.

        Returns:
            success (bool): 通信が成功したか(成功:true/失敗:false)
        """
        url = f"http://{self.server_ip}/robot_info/skip_camera_action_true"
        try:
            # APIにリクエストを送信
            response = requests.post(url)
            success = True
        except Exception as e:
            print(e)
            success = False
        return success
