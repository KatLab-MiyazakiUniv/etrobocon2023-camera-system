"""走行体状況監視モジュール.

走行体の状況を把握し続ける.
@author: aridome222
@note 参考 https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217
"""
import urllib.request
import time


def Client():
    url = 'http://127.0.0.1:8000/robot_info/state'
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
             
        # レスポンスが"notReady"の時
        if response_text == "notReady":
            print("notReady")
        # レスポンスが"wait"になった時
        elif response_text == "wait":
            print("wait")
        # レスポンスが"start"になった時
        elif response_text == "start":
            print("start")
        # レスポンスが"lap"になった時
        elif response_text == "lap":
            print("lap")
        # レスポンスが"finish"になった時
        else:
            print("finish")
            break

        # 2秒待つ
        time.sleep(2)        

    return