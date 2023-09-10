"""ロボコンスナップを攻略するモジュール.

@author: kawanoichi
"""
import os
import subprocess
import time

from detect_object import DetectObject, PROJECT_DIR_PATH
from image_processing import ImageProcessing
from official_interface import OfficialInterface


class RoboSnap:
    """ロボコンスナップクラス."""

    __IMAGE_LIST = ["FigA_1.png",
                    "FigA_2.png",
                    "FigA_3.png",
                    "FigA_4.png",
                    "FigB.png"]

    __Fig_IMAGE_B = __IMAGE_LIST[1]

    __DETECT_LABLE = {
        "Fig": 0,
        "FrontalFace": 1,
        "Profile": 2
    }

    __BASH_PATH = os.path.join(PROJECT_DIR_PATH, "copy_fig.sh")
    __IMAGE_DIR_PATH = os.path.join(PROJECT_DIR_PATH, "fig_image")

    def __init__(self,
                 raspike_ip="192.168.11.16",
                 ) -> None:
        """コンストラクタ."""
        self.raspike_ip = raspike_ip
        self.candidate_image = None

    def execute_bash(self):
        """bashファイルを実行する関数."""
        for img in self.__IMAGE_LIST:
            pass
            # args = [self.__BASH_PATH, self.raspike_ip, img]
            # try:
            #     subprocess.run(args, check=True)
            # except subprocess.CalledProcessError as e:
            #     pass

    def exist_image(self):
        """画像が送られてきたかどうかの確認関数."""
        for img in self.__IMAGE_LIST:
            img_path = os.path.join(self.__IMAGE_DIR_PATH, img)
            if os.path.exists(img_path):
                self.__IMAGE_LIST.remove(img)
                return img_path, img
        return None

    def check_bestshot(self, objects) -> int:
        """ベストショット画像らしさスコアの算出.

        信頼度は検出時にフィルターをかけているので検出したクラスと座標で判断する

        Args:
            objects: 検出した物体

        Returns:
            int: ベストショット画像らしさスコア

        NOTE:
            objectsの型について
             行数:検出数
             列数:6列([x_min, y_min, x_max, y_max, conf, cls])

            検出項目:
                0: "Fig", 1: "FrontalFace", 2: "Profile"

            スコア定義
                0 and 1: 5pt ベストショット確定(撮影動作Skip)
                0 and 2: 4pt (もしかしたらベストショット)
                0      : 3pt (ナイスショット)
                1      : 2pt
                2      : 1pt
                other  : 0pt

        TODO:
            比較要素に座標を取り組む？
            label in cls
        """
        cls = [row[5] for row in objects]
        if self.__DETECT_LABLE["Fig"] in cls \
                and self.__DETECT_LABLE["FrontalFace"] in cls:
            return 5

        if self.__DETECT_LABLE["Fig"] in cls \
                and self.__DETECT_LABLE["Profile"] in cls:
            return 4

        elif self.__DETECT_LABLE["Fig"] in cls:
            return 3

        elif self.__DETECT_LABLE["FrontalFace"] in cls:
            return 2

        elif self.__DETECT_LABLE["Profile"] in cls:
            return 1

        else:
            return 0

    def start(self) -> None:
        """ロボコンスナップを攻略する."""
        # 物体検出のパラメータはデフォルト通り
        d = DetectObject()

        sent_to_official = False
        while len(self.__IMAGE_LIST):  # 全てのファイルの物体検出が終わるまでループ
            pre_score = -1
            while True:  # 画像が見つかるまでループ
                # 画像の受信試み
                self.execute_bash()
                print()

                # 受信できたか確認
                fig_image_path, img = self.exist_image()
                if fig_image_path is not None:
                    break
                time.sleep(2)

            # 鮮明化
            processed_image_path = os.path.join(
                self.__IMAGE_DIR_PATH, "processed_"+img)
            ImageProcessing.sharpen_image(img_path=fig_image_path,
                                          save_path=processed_image_path)

            # リサイズ
            ImageProcessing.resize_img(img_path=processed_image_path,
                                       save_path=processed_image_path)

            if img == self.__Fig_IMAGE_B:
                # 配置エリアBの画像は検出せずにアップロード
                print(img, "is skip")
                # OfficialInterface.upload_snap(processed_image_path)
                continue

            # 物体検出
            save_path = os.path.join(self.__IMAGE_DIR_PATH, "detected_"+img)
            objects = d.detect_object(processed_image_path, save_path)

            # ベストショット画像らしさスコア算出
            score = self.check_bestshot(objects)

            print("score: ", score)

            if score == 5:
                # TODO:撮影動作を終了
                print("ベストショット！！")
                # OfficialInterface.upload_snap(processed_image_path)
                sent_to_official = True
                break

            elif score > pre_score:
                self.candidate_image = processed_image_path
                pre_score = score

        if sent_to_official is False:
            print("candidate_best_image")
            # OfficialInterface.upload_snap(self.candidate_best_image)


if __name__ == "__main__":
    """作業用."""
    snap = RoboSnap()
    snap.start()
    print("終了")
