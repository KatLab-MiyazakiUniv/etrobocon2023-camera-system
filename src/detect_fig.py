import torch
from pathlib import Path
import os
import numpy as np
import sys
home_directory = os.path.expanduser("~")  # noqa
PATH = os.path.join(
    home_directory, "etrobocon2023-camera-system", "machine_learning")  # noqa
sys.path.append(PATH)  # noqa
from ultralytics.utils.plotting import Annotator, colors
from models.common import DetectMultiBackend
from utils.dataloaders import LoadImages
from utils.general import (
    check_img_size, cv2, non_max_suppression, scale_boxes)
from utils.torch_utils import select_device, smart_inference_mode
from utils.augmentations import letterbox


def exit_check(path):
    """ファイル, ディレクトリが存在するかの確認パス"""
    if not os.path.exists(path):
        print(f"Error: {path} does not exist.")
        sys.exit(1)


class Detect():
    """yolov5をロボコン用に編集したクラス.
    
    ロボコン用に以下の変更を行った。
    - いらない処理の除去
    - cpuに限定させる
    - strideに合わせて画像サイズを変更する処理の除去
    """
    DEVICE = 'cpu'

    def __init__(self, 
                 weights='best.pt',
                 label_data='label_data.yaml',
                 img_size=(640, 480),
                 conf_thres=0.25,
                 iou_thres=0.45,
                 max_det=1000,
                 line_thickness=3,
                 stride=32):
        exit_check(weights)
        exit_check(label_data)
        self.weights = weights  # 重みファイルのpath
        self.label_data = label_data  # dataset.yaml path
        self.img_size = img_size  # inference size (height, width)
        self.conf_thres = conf_thres  # 信頼度閾値
        self.iou_thres = iou_thres  # NMS IOU 閾値
        self.max_det = max_det  # maximum detections per image
        self.line_thickness = line_thickness  # バウンディングボックスの線の太さ (pixels)
        self.stride = stride

    def read_image(self, img_path, auto=True):
        im0 = cv2.imread(img_path)  # BGR
        if im0 is None:
            return None, None

        # リサイズとパディング処理
        im = letterbox(im0, self.img_size, stride=self.stride,
                        auto=auto)[0]  # padded resize
        im = im.transpose((2, 0, 1))[::-1]  # BGR -> RGB
        im = np.ascontiguousarray(im)  # contiguous

        return im, im0


    def predict(self, img_path, save_path=None):
        exit_check(img_path)

        # cpuを指定
        device = select_device(Detect.DEVICE)

        # モデルの読み込み
        model = DetectMultiBackend(
            self.weights, device=device, dnn=False, data=self.label_data, fp16=False)

        stride, labels, pt = model.stride, model.names, model.pt

        # 画像のサイズを指定されたストライド（ステップ）の倍数に合わせるための関数
        self.img_size = check_img_size(self.img_size, s=stride)  # >> [640, 640]

        # モデルの初期化
        bs = 1  # batch_size
        model.warmup(imgsz=(1 if pt or model.triton else bs,
                     3, *img_size))  # warmup
                    #  3, *self.img_size))  # warmup

        # 初回ループの出力
        # img_path: /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png
        # im:画像データのNumPy配列 (3, 640, 640)
        # im0s: オリジナルの画像データ(640, 640, 3)
        # s: image 1/36 /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png:

        # for img_path, im, im0s, _, _ in dataset:
        im, im0s = self.read_image(img_path)
        print("im.shape", im.shape)
        print("im0s.shape", im0s.shape)
        # """
        # PyTorchのテンソルに変換
        im = torch.from_numpy(im).to(model.device)

        # model.fp16がTrueの場合は、テンソルを半精度浮動小数点数（float16）に変換
        # そうでない場合は、単精度浮動小数点数（float32）に変換
        im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32

        # テンソルの値を0から255の範囲から0.0から1.0の範囲にスケーリング
        im /= 255  # 0 - 255 to 0.0 - 1.0

        # もしimの形状が3次元（例：[3, 640, 640]）の場合、バッチ次元を追加して4次元のテンソルに変換
        # これは、モデルに複数の画像を一度に処理させるための操作
        if len(im.shape) == 3:
            # expand for batch dim torch.Size([3, 640, 640]) >> torch.Size([1, 3, 640, 640])
            im = im[None]

        # im: 入力画像
        # augment: データ拡張を行うかどうか
        # visualize: 可視化を行うかどうか
        # len(pred): 2
        pred = model(im, augment=False, visualize=False)

        # pred: 物体検出結果
        # conf_thres: 信頼度の閾値
        # iou_thres: IoUの閾値
        # classes: 検出するクラスのリスト
        # agnostic_nms: NMS(Non-Maximum Suppression)を適用するか
        # max_det: 最大検出数
        # NMS(Non-Maximum Suppression)関数
        # 重なりのある複数の物体検出結果をフィルタリング
        pred = non_max_suppression(
            pred, self.conf_thres, self.iou_thres, max_det=self.max_det, classes=None, agnostic=False)

        # 検出結果の処理
        for det in pred:  # det:検出結果
            print(Path(img_path).name, " 検出数", len(det), )

            # im0: 入力画像
            im0 = im0s.copy()

            # img_path >> /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png
            img_path = Path(img_path)  # 入力と出力が同じだが、意味あるの？

            # save_path >> runs/detect/result22/image1.png
            # save_path = os.img_path.join(str(save_dir), str(img_path.name))  # im.jpg

            # 画像にバウンディングボックスやラベルなどのアノテーションを追加
            annotator = Annotator(
                im0, line_width=self.line_thickness, example=str(labels))

            if len(det):
                # バウンディングボックス座標を画像サイズから別のサイズに変換
                det[:, :4] = scale_boxes(
                    im.shape[2:], det[:, :4], im0.shape).round()

                # Write results
                # バウンディングボックスの座標(xyxy：[x_min, y_min, x_max, y_max] 形式)、信頼度(conf)、クラスID(cls)
                for *xyxy, conf, cls in reversed(det):
                    if save_path:
                        c = int(cls)  # クラスid

                        label = f'{labels[c]} {conf:.2f}'
                        # label >> front 0.94
                        #
                        # annotator.box_label():画像にバウンディングボックスとラベルを追加
                        # colors():検出されたクラスのインデックスに基づいて、一意の色を生成。
                        #         True パラメータは、色をランダムに選択することを指示。
                        #         異なるクラスは異なる色で表示されます。
                        annotator.box_label(xyxy, label, color=colors(c, True))

            # 検出結果を含む画像を保存
            im0 = annotator.result()
            if save_path:
                cv2.imwrite(save_path, im0)


if __name__ == '__main__':
    image_path = '/home/kawano/etrobocon2023-camera-system/machine_learning/test_image.png'
    save_path = '/home/kawano/etrobocon2023-camera-system/machine_learning/detect_test_image.png'
    weights = '/home/kawano/etrobocon2023-camera-system/machine_learning/best.pt'
    label_data = '/home/kawano/etrobocon2023-camera-system/machine_learning/label_data.yaml'
    d = Detect(weights=weights, label_data=label_data)
    d.predict(image_path, save_path)
    print('完了')
