"""ロボコンスナップを攻略するモジュール.

@author: kawanoichi
"""
import os
import time
import numpy as np

from detect_object import DetectObject, PROJECT_DIR_PATH
from image_processing import ImageProcessing
from official_interface import OfficialInterface
from client import Client

class RoboSnap:
    """ロボコンスナップ攻略クラス."""

    img_list = ["FigA_1.png",
                "FigA_2.png",
                "FigA_3.png",
                "FigA_4.png",
                "FigB.png"]

    fig_img_B = "FigB.png"

    # NOTE:powershellの場合、絶対パスでbashファイルが実行できない？
    #      よってcamera-system下での実装に対応
    bash_path = "copy_fig.sh"
    img_dir_path = os.path.join(PROJECT_DIR_PATH, "fig_image")

    def __init__(self,
                 raspike_ip="192.168.11.16",
                 ) -> None:
        """コンストラクタ.

        Args:
            raspike_ip: 走行体のIPアドレス
        """
        self.raspike_ip = raspike_ip

    def scp_fig_image(self) -> None:
        """走行体からフィグ画像を取得するbashファイルを実行する関数."""
        for img in self.img_list:
            bash_command = f"bash {self.bash_path} {self.raspike_ip} {img}"
            try:
                os.system(bash_command)
            except Exception:
                # 何回も実行するので、エラー文は省略
                pass

    def exist_image(self) -> (str, str):
        """画像が送られてきたかどうかの確認関数.

        Returns:
            img_name(str): 画像ファイル名
            img_path(str): 画像パス
        """
        for img_name in self.img_list:
            img_path = os.path.join(self.img_dir_path, img_name)
            if os.path.exists(img_path):
                self.img_list.remove(img_name)
                return img_name, img_path
        return None, None

    def check_bestshot(self, objects) -> int:
        """ベストショット画像らしさスコアの算出.

        信頼度は検出時にフィルターをかけているので検出したクラスと座標で判断する

        Args:
            objects: 検出した物体

        Returns:
            int: ベストショット画像らしさスコア

        NOTE:
            objectsの型について:
                行数: 検出数
                列数: 6列([x_min, y_min, x_max, y_max, conf, cls])

            検出項目(ラベル):
                0: "Fig" - ミニフィグの全身
                1: "FrontalFace" - ミニフィグの正面顔
                2: "Profile" - ミニフィグの横顔

            スコア定義:
                0 and 1 : 5pt ベストショット確定(撮影動作Skip)
                0 and 2 : 4pt (もしかしたらベストショット)
                0       : 3pt (ナイスショット)
                1       : 2pt
                2       : 1pt
                others  : 0pt
        """
        # 検出されたobjectがなかった場合
        if len(objects) == 0:
            return 0

        # objectをラベルごとに仕分け
        objects_np = np.array(objects)
        index_of_fig = np.where(objects_np[:, 5] == 0)
        index_of_frontalface = np.where(objects_np[:, 5] == 1)
        index_of_profile = np.where(objects_np[:, 5] == 2)

        if index_of_fig[0].size > 0 \
                and index_of_frontalface[0].size > 0:
            # 2つのボックスが重なっているかを確認
            for fig in objects_np[index_of_fig]:
                for frontalface in objects_np[index_of_frontalface]:
                    # (x1_min < x2_max and x2_min < x1_max) \
                    #     and (y2_min < y1_max and y1_min < y2_max)
                    if fig[0] < frontalface[2] and \
                            frontalface[0] < fig[2] and \
                            frontalface[1] < fig[3] and \
                            fig[1] < frontalface[3]:
                        return 5
            # 重なってない場合、"FrontalFace"を信用しない
            return 3

        elif index_of_fig[0].size > 0 \
                and index_of_profile[0].size > 0:
            # 2つのボックスが重なっているかを確認
            for fig in objects_np[index_of_fig]:
                for profile in objects_np[index_of_profile]:
                    # (x1_min < x2_max and x2_min < x1_max) \
                    #     and (y2_min < y1_max and y1_min < y2_max)
                    if fig[0] < profile[2] and \
                            profile[0] < fig[2] and \
                            profile[1] < fig[3] and \
                            fig[1] < profile[3]:
                        return 4
            # 重なってない場合、"Profile"を信用しない
            return 3

        elif index_of_fig[0].size > 0:
            return 3

        elif index_of_frontalface[0].size > 0:
            return 2

        elif index_of_profile[0].size > 0:
            return 1
        else:
            return 0

    def start_snap(self) -> None:
        """ロボコンスナップを攻略する."""
        # 物体検出のパラメータはデフォルト通り
        d = DetectObject()

        sent_to_official = False
        for _ in range(len(self.img_list)):
            max_score = -1  # score初期値
            while True:  # 画像が見つかるまでループ
                # 画像の受信試み
                self.scp_fig_image()

                # 受信できたか確認
                img_name, img_path = self.exist_image()
                if img_path is not None:
                    break
                time.sleep(2)
            # 鮮明化
            processed_img_path = os.path.join(
                self.img_dir_path, "processed_"+img_name)
            ImageProcessing.sharpen_image(img_path=img_path,
                                          save_path=processed_img_path)

            # リサイズ
            ImageProcessing.resize_img(img_path=processed_img_path,
                                       save_path=processed_img_path)

            if img_name == self.fig_img_B:
                # 配置エリアBの画像は検出せずにアップロード
                OfficialInterface.upload_snap(processed_img_path)
                continue

            # 物体検出
            detected_img_path = os.path.join(
                self.img_dir_path, "detected_"+img_name)
            objects = d.detect_object(img_path=processed_img_path,
                                      save_path=detected_img_path)

            # ベストショット画像らしさスコア算出
            try:
                score = self.check_bestshot(objects)
            except Exception as e:
                score = 0

            # ベストショット確定だと判断した場合
            if score == 5:
                OfficialInterface.upload_snap(processed_img_path)
                sent_to_official = True
                client = Client(self.raspike_ip)
                client.set_true_camera_action_skip()
                break

            elif score > max_score:
                # 候補画像の更新
                candidate_img_path = processed_img_path
                max_score = score

        # ベストショット確定と判断できる画像がなかった場合
        if sent_to_official is False:
            # 候補画像のアップロード
            OfficialInterface.upload_snap(candidate_img_path)


if __name__ == "__main__":
    """作業用."""
    snap = RoboSnap()
    snap.start_snap()
    print("終了")
