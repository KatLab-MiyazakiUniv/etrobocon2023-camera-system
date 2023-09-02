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
import warnings

script_dir = os.path.dirname(os.path.abspath(__file__))  # noqa
YOLO_PATH = os.path.join(script_dir, "..", "yolo")  # noqa
sys.path.append(YOLO_PATH)  # noqa
YOLO_PATH = Path(YOLO_PATH)  # noqa
from models.common import DetectMultiBackend
from utils.general import (
    check_img_size, cv2, non_max_suppression, scale_boxes)
from utils.torch_utils import select_device
from utils.augmentations import letterbox

IMAGE_PATH = os.path.join(script_dir, "..", "fig_image")
IMAGE_PATH = Path(IMAGE_PATH)


class DetectedObject():
    """yolov5(物体検出)をロボコン用に編集したクラス."""

    DEVICE = 'cpu'
    IMG_SIZE = (640, 480)

    def __init__(self,
                 weights=YOLO_PATH/'learned_fig_weight.pt',
                 label_data=YOLO_PATH/'fig_label.yaml',
                 conf_thres=0.6,
                 iou_thres=0.45,
                 max_det=10,
                 line_thickness=3,
                 stride=32):
        """コンストラクタ.

        Args:
            weights (str): 重みファイルパス
            label_data (str): ラベルを記述したファイルパス
            conf_thres (float): 信頼度閾値
            iou_thres (float): NMS IOU 閾値
            max_det (int): 最大検出数
            line_thickness (int): カメラID
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
    def check_exist(path) -> bool:
        """ファイル, ディレクトリが存在するかの確認.

        Args:
            path (str): ファイルまたはディレクトリのパス

        Raises:
            FileNotFoundError: ファイルが見つからない場合に発生
        """
        if not os.path.exists(path):
            warnings.warn(f"'{path}' does not exist", Warning)
            return False
        return True

    def detect_objects(self, img_path=IMAGE_PATH/'test_image.png', save_path=None) -> list:
        """物体の検出を行う関数.

        Args:
            img_path(str): 物体検出を行う画像パス
            save_path(str): 検出結果の画像保存パス
                            Noneの場合、保存しない
        Returns:
            bool: 入力ファイルがなかった場合、Falseを返す
            list: 正常に物体検出を行った場合、予測結果を返す
        """
        if not self.check_exist(img_path):
            return False

        # cpuを指定
        device = select_device(DetectedObject.DEVICE)

        # モデルの読み込み
        model = DetectMultiBackend(self.weights,
                                   device=device,
                                   dnn=False,
                                   data=self.label_data,
                                   fp16=False)

        stride, labels, pt = model.stride, model.names, model.pt

        # 画像のサイズを指定されたストライド（ステップ）の倍数に合わせるための関数
        img_size = check_img_size(
            DetectedObject.IMG_SIZE, s=stride)  # >> [640, 640]

        # モデルの初期化
        batch_size = 1
        model.warmup(
            imgsz=(1 if pt or model.triton else batch_size, 3, *img_size))

        # 画像の読み込み
        original_img = cv2.imread(img_path)  # BGR

        # パディング処理
        img = letterbox(original_img, DetectedObject.IMG_SIZE, stride=self.stride,
                        auto=True)[0]
        # BGR -> RGB
        img = img.transpose((2, 0, 1))[::-1]

        # 連続したメモリ領域に変換
        img = np.ascontiguousarray(img)

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
        if save_path:
            for det in pred:  # det:検出結果
                print(Path(img_path).name, " 検出数", len(det), )

                save_img = original_img.copy()

                # 画像にバウンディングボックスやラベルなどのアノテーションを追加
                annotator = Annotator(
                    save_img, line_width=self.line_thickness, example=str(labels))

                if len(det):
                    # バウンディングボックス座標を画像サイズから別のサイズに変換
                    det[:, :4] = scale_boxes(
                        img.shape[2:], det[:, :4], save_img.shape).round()

                    # xyxy: バウンディングボックスの座標([x_min, y_min, x_max, y_max] 形式)
                    # conf: 信頼度
                    # cls: クラスID
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)  # クラスid
                        label = f'{labels[c]} {conf:.2f}'
                        # 画像にバウンディングボックスとラベルを追加
                        annotator.box_label(xyxy, label, color=colors(c, True))

            # 検出結果を含む画像を保存
            save_img = annotator.result()
            cv2.imwrite(save_path, save_img)
            print("保存")

        return pred


if __name__ == '__main__':
    """作業用."""
    save_path = os.path.join(str(IMAGE_PATH), "detect_test_image.png")
    d = DetectedObject()
    d.detect_objects(save_path=save_path)

    print("完了")
