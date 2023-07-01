"""走行体状況監視モジュール.

走行体の状況を把握し続ける.
@author: aridome222
@note 参考 https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217
"""
import urllib.request
import time


class Client:
    """走行体がゴールするまでサーバにリクエストを送り続け、ロボットの状況を把握するクラス."""

    def client(self):
        """走行体の状況を把握するために、サーバにリクエストを送る."""
        # 'http://～:8000/robot_info/state'の"～"部分は、走行体側のIPアドレスを指定する
        # et2023@katlabなら192.168.11.16、et2023@katlab2なら192.168.11.17
        url = 'http://192.168.11.17:8000/robot_info/state'
        req = urllib.request.Request(url)
        response_text = ""

        while True:
            # 指定したurlにGETリクエストを投げてレスポンスを受け取る
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

            # レスポンスが"finish"になった時、終了する。
            if response_text == "finish":
                print(response_text)
                break
            else:
                print(response_text)

            # 2秒待つ
            time.sleep(2)
