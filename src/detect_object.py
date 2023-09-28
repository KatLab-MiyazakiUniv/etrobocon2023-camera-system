"""物体検出を行うモジュール.

ベストショット画像を選択するための物体検出を行う。

NOTE:
    'learned_fig_weight.pt'は以下にあります。
    https://drive.google.com/drive/folders/1aUrB3Pj4hzt624SlJv8h1vVOBopAr48l
    etrobocon2023-camera-system/yolo/の中にダウンロードしてください

参考コード:
    https://github.com/ultralytics/yolov5
@author: kawanoichi
"""

import torch
from pathlib import Path
import os
import numpy as np
import sys
from ultralytics.utils.plotting import Annotator, colors

script_dir = os.path.dirname(os.path.abspath(__file__))  # noqa
YOLO_PATH = os.path.join(script_dir, "..", "yolo")  # noqa
sys.path.append(YOLO_PATH)  # noqa
YOLO_PATH = Path(YOLO_PATH)  # noqa
from models.common import DetectMultiBackend
from utils.general import (
    check_img_size, cv2, non_max_suppression, scale_boxes)
from utils.torch_utils import select_device
from utils.augmentations import letterbox

PROJECT_DIR_PATH = os.path.dirname(script_dir)
IMAGE_DIR_PATH = Path(os.path.join(PROJECT_DIR_PATH, "fig_image"))


class DetectObject():
    """yolov5(物体検出)をロボコン用に編集したクラス."""

    __DEVICE = 'cpu'
    __IMG_SIZE = (640, 480)

    def __init__(self,
                 weights=YOLO_PATH/'learned_fig_weight_ver2.pt',
                #  weights=YOLO_PATH/'learned_fig_weight.pt',
                 label_data=YOLO_PATH/'fig_label.yaml',
                 conf_thres=0.6,
                 iou_thres=0.45,
                 max_det=10,
                 line_thickness=1,
                 stride=32):
        """コンストラクタ.

        Args:
            weights (str): 重みファイルパス
            label_data (str): ラベルを記述したファイルパス
            conf_thres (float): 信頼度閾値
            iou_thres (float): NMS IOU 閾値
            max_det (int): 最大検出数
            line_thickness (int): バウンディングボックスの太さ
            stride (int): ストライド
        """
        self.check_exist(weights)
        self.check_exist(label_data)
        self.weights = str(weights)
        self.label_data = str(label_data)
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.max_det = max_det
        self.line_thickness = line_thickness
        self.stride = stride

    @staticmethod
    def check_exist(path: str) -> None:
        """ファイル, ディレクトリが存在するかの確認.

        Args:
            path (str): ファイルまたはディレクトリのパス

        raise:
            FileNotFoundError: ファイルがない場合に発生
        """
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"'{path}' is not found")

        except FileNotFoundError as e:
            print("Error:", e)

    def detect_object(self,
                      img_path=IMAGE_DIR_PATH/'test_image.png',
                      save_path=None) -> list:
        """物体の検出を行う関数.

        Args:
            img_path(str): 物体検出を行う画像パス
            save_path(str): 検出結果の画像保存パス
                            Noneの場合、保存しない
        Returns:
            list: 検出したオブジェクト
        """
        self.check_exist(img_path)

        # cpuを指定
        device = select_device(self.__DEVICE)

        # モデルの読み込み
        model = DetectMultiBackend(self.weights,
                                   device=device,
                                   dnn=False,
                                   data=self.label_data,
                                   fp16=False)

        stride, labels, pt = model.stride, model.names, model.pt

        # 画像のサイズを指定されたストライド（ステップ）の倍数に合わせるための関数
        img_size = check_img_size(
            self.__IMG_SIZE, s=stride)  # >> [640, 640]

        # モデルの初期化
        batch_size = 1
        model.warmup(
            imgsz=(1 if pt or model.triton else batch_size, 3, *img_size))

        # 画像の読み込み
        original_img = cv2.imread(img_path)  # BGR

        # パディング処理
        img = letterbox(original_img,
                        self.__IMG_SIZE,
                        stride=self.stride,
                        auto=True)[0]
        img = img.transpose((2, 0, 1))[::-1]  # BGR -> RGB
        img = np.ascontiguousarray(img)  # 連続したメモリ領域に変換
        img = torch.from_numpy(img).to(model.device)  # PyTorchのテンソルに変換
        img = img.half() if model.fp16 else img.float()  # uint8 to fp16/32

        # スケーリング
        img /= 255  # 0 - 255 to 0.0 - 1.0

        # torch.Size([3, 640, 640]) >> torch.Size([1, 3, 640, 640])
        if len(img.shape) == 3:
            img = img[None]

        # 検出
        pred = model(img, augment=False, visualize=False)

        # 非最大値抑制 (NMS) により重複検出を拒否
        pred = non_max_suppression(pred,
                                   self.conf_thres,  # 信頼度の閾値
                                   self.iou_thres,  # IoUの閾値
                                   max_det=self.max_det,  # 保持する最大検出数
                                   classes=None,  # 検出するクラスのリスト
                                   agnostic=False  # Trueの場合、クラスを無視してNMSを実行
                                   )

        # 検出結果を画像に描画
        objects = pred[0]
        print(Path(img_path).name, " 検出数", len(objects))

        save_img = original_img.copy()

        # 画像にバウンディングボックスやラベルなどのアノテーションを追加
        annotator = Annotator(save_img,
                              line_width=self.line_thickness,
                              example=str(labels))

        if len(objects):
            # バウンディングボックスをimgサイズからsave_imgサイズに再スケールします
            objects[:, :4] = scale_boxes(
                img.shape[2:], objects[:, :4], save_img.shape).round()

            if save_path is not None:
                # xyxy: バウンディングボックスの座標([x_min, y_min, x_max, y_max] 形式)
                # conf: 信頼度
                # cls: クラスID
                for *xyxy, conf, cls in reversed(objects):
                    c = int(cls)
                    label = f'{labels[int(cls)]} {conf:.2f}'
                    # 画像にバウンディングボックスとラベルを追加
                    annotator.box_label(xyxy, label, color=colors(c, True))

                # 検出結果を含む画像を保存
                save_img = annotator.result()
                cv2.imwrite(save_path, save_img)

        """
        NOTE:
            objectsの型について
             行数:検出数
             列数:6列([x_min, y_min, x_max, y_max, conf, cls])
        """
        return objects.tolist()


if __name__ == '__main__':
    """作業用.
    $ poetry run python ./src/detect_object.py
        --img_path fig_image/test_image.png
    """
    import argparse
    save_path = os.path.join(str(IMAGE_DIR_PATH), "detect_test_image.png")

    parser = argparse.ArgumentParser(description="リアカメラに関するプログラム")

    parser.add_argument("-wpath", "--weights", type=str,
                        default=YOLO_PATH/'learned_fig_weight.pt',
                        help='重みファイルパス')
    parser.add_argument("-label", "--label_data", type=str,
                        default=YOLO_PATH/'fig_label.yaml',
                        help='ラベルを記述したファイルパス')
    parser.add_argument("-conf", "--conf_thres", type=int,
                        default=0.6, help='信頼度閾値')
    parser.add_argument("-iou", "--iou_thres", type=int,
                        default=0.45, help='IOU 閾値')
    parser.add_argument("--max_det", type=int, default=10, help='最大検出数')
    parser.add_argument("--line_thickness", type=int,
                        default=1, help='バウンディングボックスの太さ')
    parser.add_argument("--stride", type=int, default=32, help='ストライド')
    parser.add_argument("-img", "--img_path", type=str,
                        default=IMAGE_DIR_PATH/'FigA_3.png', help='入力画像')
    parser.add_argument("-spath", "--save_path", type=str,
                        default=save_path, help='検出画像の保存先. Noneの場合保存しない')
    args = parser.parse_args()

    d = DetectObject(args.weights,
                     args.label_data,
                     args.conf_thres,
                     args.iou_thres,
                     args.max_det,
                     args.line_thickness,
                     args.stride)

    objects = d.detect_object(args.img_path, args.save_path)
    print("objects\n", objects)

    print("完了")
