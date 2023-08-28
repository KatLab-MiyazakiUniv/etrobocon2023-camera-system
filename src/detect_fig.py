"""物体検出を行うモジュール.

ベストショット画像を選択するための物体検出を行う。

NOTE:
    'learned_weight.pt'は以下にあります。
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
YOLO_PATH = os.path.join("..", "etrobocon2023-camera-system", "yolo")  # noqa
sys.path.append(YOLO_PATH)  # noqa
YOLO_PATH = Path(YOLO_PATH)  # noqa
from models.common import DetectMultiBackend
from utils.general import (
    check_img_size, cv2, non_max_suppression, scale_boxes)
from utils.torch_utils import select_device
from utils.augmentations import letterbox

IMAGE_PATH = os.path.join("..", "etrobocon2023-camera-system", "fig_image")  # noqa
IMAGE_PATH = Path(IMAGE_PATH)  # noqa


def check_exists(path):
    """ファイル, ディレクトリが存在するかの確認.

    Args:
        path (str): ファイルまたはディレクトリのパス
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"'{path}' does not found\n")

    except FileNotFoundError as e:
        print("\nError:", e)


class Detect():
    """yolov5(物体検出)をロボコン用に編集したクラス."""

    DEVICE = 'cpu'
    IMG_SIZE = (640, 480)

    def __init__(self,
                 img_path=IMAGE_PATH / 'test_image.png',
                 weights=YOLO_PATH / 'learned_weight.pt',
                 label_data=YOLO_PATH / 'label_data.yaml',
                 conf_thres=0.6,
                 iou_thres=0.45,
                 max_det=10,
                 line_thickness=3,
                 stride=32):
        """コンストラクタ.

        Args:
            img_path (str): 画像パス
            weights (str): 重みファイルパス
            label_data (str): ラベルを記述したファイルパス
            conf_thres (float): 信頼度閾値
            iou_thres (float): NMS IOU 閾値
            max_det (int): 最大検出数
            line_thickness (int): カメラID
            stride (int): ストライド
        """
        check_exists(img_path)
        check_exists(weights)
        check_exists(label_data)
        self.img_path = str(img_path)
        self.weights = str(weights)
        self.label_data = str(label_data)
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.max_det = max_det
        self.line_thickness = line_thickness
        self.stride = stride

    def read_image(self, auto=True):
        """画像を読み込む関数.

        Args:
            img_path: 画像パス
        Returns:
            pred: 予測結果
        """
        im0 = cv2.imread(self.img_path)  # BGR

        # リサイズとパディング処理
        im = letterbox(im0, Detect.IMG_SIZE, stride=self.stride,
                       auto=auto)[0]
        # BGR -> RGB
        im = im.transpose((2, 0, 1))[::-1]
        # 連続したメモリ領域に変換
        im = np.ascontiguousarray(im)

        return im, im0

    def detect(self, save_path=None):
        """物体の検出を行う関数.

        Args:
            save_path(str): 検出結果の画像保存パス
                            Noneの場合、保存しない
        Returns:
            im: パディング処理を行った入力画像
            im0: 入力画像
        """
        # cpuを指定
        device = select_device(Detect.DEVICE)

        # モデルの読み込み
        model = DetectMultiBackend(self.weights,
                                   device=device,
                                   dnn=False,
                                   data=self.label_data,
                                   fp16=False)

        stride, labels, pt = model.stride, model.names, model.pt

        # 画像のサイズを指定されたストライド（ステップ）の倍数に合わせるための関数
        img_size = check_img_size(Detect.IMG_SIZE, s=stride)  # >> [640, 640]

        # モデルの初期化
        batch_size = 1
        model.warmup(
            imgsz=(1 if pt or model.triton else batch_size, 3, *img_size))

        # 画像の読み込み
        im, im0s = self.read_image()

        im = torch.from_numpy(im).to(model.device)  # PyTorchのテンソルに変換
        im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32

        # スケーリング
        im /= 255  # 0 - 255 to 0.0 - 1.0

        # torch.Size([3, 640, 640]) >> torch.Size([1, 3, 640, 640])
        if len(im.shape) == 3:
            im = im[None]

        # 検出
        pred = model(im, augment=False, visualize=False)

        # 非最大値抑制 (NMS) により重複検出を拒否
        pred = non_max_suppression(pred,
                                   self.conf_thres,  # 信頼度の閾値
                                   self.iou_thres,  # IoUの閾値
                                   max_det=self.max_det,  # 保持する最大検出数
                                   classes=None,  # 検出するクラスのリスト
                                   agnostic=False  # Trueの場合、クラスを無視してNMSを実行
                                   )

        # 検出結果を画像に描画
        if save_path:
            for det in pred:  # det:検出結果
                print(Path(self.img_path).name, " 検出数", len(det), )

                im0 = im0s.copy()

                # 画像にバウンディングボックスやラベルなどのアノテーションを追加
                annotator = Annotator(
                    im0, line_width=self.line_thickness, example=str(labels))

                if len(det):
                    # バウンディングボックス座標を画像サイズから別のサイズに変換
                    det[:, :4] = scale_boxes(
                        im.shape[2:], det[:, :4], im0.shape).round()

                    # xyxy: バウンディングボックスの座標([x_min, y_min, x_max, y_max] 形式)
                    # conf: 信頼度
                    # cls: クラスID
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)  # クラスid
                        label = f'{labels[c]} {conf:.2f}'
                        # 画像にバウンディングボックスとラベルを追加
                        annotator.box_label(xyxy, label, color=colors(c, True))

            # 検出結果を含む画像を保存
            check_exists(os.path.dirname(save_path))

            im0 = annotator.result()
            cv2.imwrite(save_path, im0)

        return pred


if __name__ == '__main__':
    """作業用."""
    save_path = os.path.join(str(IMAGE_PATH), "detect_test_image.png")
    d = Detect()
    d.detect(save_path)
