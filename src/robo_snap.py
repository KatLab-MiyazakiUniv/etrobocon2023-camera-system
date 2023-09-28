"""ロボコンスナップを攻略するモジュール.

@author: kawanoichi
"""
import os
import time
import numpy as np
import shutil

from detect_object import DetectObject, PROJECT_DIR_PATH
from image_processing import ImageProcessing
from official_interface import OfficialInterface
from client import Client


class RoboSnap:
    """ロボコンスナップ攻略クラス."""

    # NOTE:FigB.pngを優先したいのでlistの最初
    img_list = [
        "FigB.png",
        "FigA_1.png",
        "FigA_2.png",
        "FigA_3.png",
        "FigA_4.png"]

    fig_img_B = "FigB.png"

    # NOTE:powershellの場合、絶対パスでbashファイルが実行できない？
    #      よってcamera-system下での実装に対応
    bash_path = "copy_fig.sh"
    img_dir_path = os.path.join(PROJECT_DIR_PATH, "fig_image")

    def __init__(self,
                 raspike_ip="172.20.1.1",
                 ) -> None:
        """コンストラクタ.

        Args:
            raspike_ip: 走行体のIPアドレス
        """
        self.raspike_ip = raspike_ip

        self.fig_B_img_path = None
        self.successful_send_fig_B = False
        self.best_shot_img = None
        self.successful_send_best_shot = False
        self.candidate_img = None
        self.candidate_img_path = None
        self.successful_send_candidate = False

    def set_up(self) -> None:
        """画像を入れるディレクトリを作り直す関数."""
        if self.check_exist(self.img_dir_path):
            shutil.rmtree(self.img_dir_path)
        os.mkdir(self.img_dir_path)

    def scp_fig_image(self) -> str:
        """走行体からフィグ画像を取得するbashファイルを実行する関数.

        Returns:
            img_name(str): ファイル(画像)名
        """
        for img_name in self.img_list:
            bash_command = \
                f"bash {self.bash_path} {self.raspike_ip} {img_name}"
            try:
                os.system(bash_command)

                # 受信できたか確認
                img_path = os.path.join(self.img_dir_path, img_name)
                if not self.check_exist(img_path):
                    continue
                else:
                    self.img_list.remove(img_name)
                    return img_name, img_path

            except Exception:
                # 何回も実行するので、エラー文は省略
                continue
        return None, None

    def check_exist(self, path) -> bool:
        """ファイルもしくはディレクトリが存在するか確認する関数.

        以下の時に使用する
        - self.img_dir_pathの作り直し
        - 画像が送られてきたかどうかの確認

        Returns:
            bool: 画像の有無
        """
        return os.path.exists(path)

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

    def show_result(self):
        """最終結果を表示する."""
        print("\n- 実行結果")
        print(f"-      FigB Image: {str(self.fig_img_B):>10},  Upload:{str(self.successful_send_fig_B):>10}")  # noqa
        print(f"- Best Shot Image: {str(self.best_shot_img):>10},  Upload:{str(self.successful_send_best_shot):>10}")  # noqa
        print(f"- Candidate Image: {str(self.candidate_img):>10},  Upload:{str(self.successful_send_candidate):>10}\n")  # noqa

    def start_snap(self) -> None:
        """ロボコンスナップを攻略する."""

        # 画像を格納するディレクトリの作成
        self.set_up()

        # 物体検出のパラメータはデフォルト通り
        d = DetectObject()

        try:
            for _ in range(len(self.img_list)):
                max_score = -1  # score初期値
                while True:  # 画像が見つかるまでループ
                    # 画像の受信試み
                    img_name, img_path = self.scp_fig_image()

                    if img_name is not None:
                        break

                    time.sleep(2)

                # 配置エリアBの画像を取得した時の処理
                if img_name == self.fig_img_B:
                    self.fig_B_img_path = img_path
                    # 配置エリアBの画像は検出せずにアップロード
                    if OfficialInterface.upload_snap(self.fig_B_img_path):
                        self.successful_send_fig_B = True
                    # 配置エリアAで画像をuploadしている場合、終了する.
                    if self.successful_send_best_shot:
                        break
                    continue

                # 物体検出
                detected_img_path = os.path.join(
                    self.img_dir_path, "detected_"+img_name)
                try:
                    objects = d.detect_object(img_path=img_path,
                                              save_path=detected_img_path)
                except Exception as e:
                    objects = []

                # ベストショット画像らしさスコア算出
                try:
                    score = self.check_bestshot(objects)
                except Exception as e:
                    score = 0

                # ベストショット確定だと判断した場合
                if score == 5:
                    self.best_shot_img = img_name
                    # 候補画像のアップロード
                    if OfficialInterface.upload_snap(img_path):
                        # Skipフラグを立てる
                        client = Client(self.raspike_ip)
                        success = client.set_true_camera_action_skip()

                        self.successful_send_best_shot = True

                    if success:
                        print("Success Skip Flag")
                    else:
                        print("Failed Skip Flag")

                    # 配置エリアA,Bで画像をuploadしている場合、終了する.
                    # NOTE: successful_send_best_shotも条件に入れることで
                    #       upload失敗時、候補画像のuploadを試みる
                    if self.successful_send_best_shot and\
                            self.successful_send_fig_B:
                        break
                    continue

                elif score > max_score:
                    # 候補画像の更新
                    self.candidate_img = img_name
                    self.candidate_img_path = img_path
                    max_score = score

            # ベストショット確定と判断できる画像がなかった場合
            if self.successful_send_best_shot is False:
                # 候補画像のアップロード
                if OfficialInterface.upload_snap(self.candidate_img_path):
                    self.successful_send_candidate = True
        finally:
            self.show_result()
            change_flag = False
            if (self.candidate_img_path is not None) and \
                    (self.successful_send_candidate is False):
                print("競技システムへのUpload")
                if OfficialInterface.upload_snap(self.candidate_img_path):
                    self.successful_send_candidate = True
                    change_flag = True

            if (self.fig_B_img_path is not None) and \
                    (self.successful_send_fig_B is False):
                print("競技システムへのUpload")
                if OfficialInterface.upload_snap(self.fig_B_img_path):
                    self.successful_send_fig_B = True
                    change_flag = True

            if change_flag:
                self.show_result()


if __name__ == "__main__":
    """作業用."""
    snap = RoboSnap()
    snap.start_snap()
