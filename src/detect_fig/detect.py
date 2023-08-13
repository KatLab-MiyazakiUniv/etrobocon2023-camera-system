from utils.torch_utils import select_device, smart_inference_mode
from utils.general import (Profile, check_img_size,
                           cv2, non_max_suppression, scale_boxes)
from utils.dataloaders import LoadImages
from models.common import DetectMultiBackend
from ultralytics.utils.plotting import Annotator, colors, save_one_box
import argparse
import os
from pathlib import Path

import torch


@smart_inference_mode()
def run(
        weights='yolov5s.pt',  # 重みファイルのpath
        source='data/images',  # 予測を行う画像データ
        data='data/data.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        project='runs/detect',  # 結果の保存先path
        line_thickness=3,  # バウンディングボックスの線の太さ (pixels)
        vid_stride=1,  # video frame-rate stride
):
    # source = str(source)

    if not nosave and not source.endswith('.txt'):
        save_img = True
    else:
        save_img = False

    # 保存先ディレクトリがなければ作成
    save_dir = os.path.join(project, 'result')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:
        save_dir += str(len(os.listdir(project))+1)
        print("save_dir", save_dir)
        os.makedirs(save_dir, exist_ok=True)

    # Load model
    device = select_device(device)  # >> cuda:0

    model = DetectMultiBackend(
        weights, device=device, dnn=False, data=data, fp16=False)

    """
    stride 32
    labels {0: 'front', 1: 'back', 2: 'right', 3: 'left'}
    pt True
    """
    stride, labels, pt = model.stride, model.names, model.pt

    # 画像のサイズを指定されたストライド（ステップ）の倍数に合わせるための関数
    imgsz = check_img_size(imgsz, s=stride)  # >> [640, 640]

    # Dataloader
    bs = 1  # batch_size
    dataset = LoadImages(source, img_size=imgsz,
                         stride=stride, auto=pt, vid_stride=vid_stride)

    # Run inference
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    seen, dt = 0, (Profile(), Profile(), Profile())

    """初回ループの出力
    path: /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png
    im:画像データのNumPy配列 (3, 640, 640)
    im0s: オリジナルの画像データ(640, 640, 3)
    vid_cap: None
    s: image 1/36 /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png: 
    """
    for path, im, im0s, _, s in dataset:
        # dt[0]: オリジナルの画像データ
        # TODO: withを消していいと思うが、その時はdtにいらない要素がある？
        with dt[0]:
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

        # Inference
        with dt[1]:
            """
            im: 入力画像
            augment: データ拡張を行うかどうか
            visualize: 可視化を行うかどうか
            len(pred): 2
            """
            pred = model(im, augment=False, visualize=False)

        # NMS
        with dt[2]:
            """
            non_max_suppression(): 非最大値抑制を実行する関数
            pred: 物体検出結果
            conf_thres: 信頼度の閾値
            iou_thres: IoUの閾値
            classes: 検出するクラスのリスト
            agnostic_nms: クラスに関係なくNMSを適用するかどうかのフラグ
            max_det: 最大検出数
            len(pred): 1
            """
            pred = non_max_suppression(
                pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Process predictions(検出結果の処理)
        for i, det in enumerate(pred):  # det:検出結果
            # print("検出数", len(det))

            seen += 1

            # p: ファイルパス, im0: 入力画像, frame: フレーム番号
            p, im0 = path, im0s.copy()

            # p >> /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png
            p = Path(p)  # 入力と出力が同じだが、意味あるの？

            # save_path >> runs/detect/result22/image1.png
            save_path = os.path.join(str(save_dir), str(p.name))  # im.jpg

            # before
            # image 1/36 /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png:
            # after
            # image 1/36 /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png: 640x640
            s += '%gx%g ' % im.shape[2:]  # print string

            # 画像にバウンディングボックスやラベルなどのアノテーションを追加
            annotator = Annotator(
                im0, line_width=line_thickness, example=str(labels))

            if len(det):
                # バウンディングボックス座標を画像サイズから別のサイズに変換
                det[:, :4] = scale_boxes(
                    im.shape[2:], det[:, :4], im0.shape).round()

                # 検出された物体のクラスと数を文字列としてフォーマット
                # det[:, 5]は検出したクラスID
                for c in det[:, 5].unique():
                    # 特定のクラスの検出数を計測
                    n = (det[:, 5] == c).sum()  # detections per class

                    # {'s' * (n > 1)}は、検出数が複数の場合にクラス名の末尾に "s" を追加
                    # s >> image 1/36 /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png: 640x640
                    s += f"{n} {labels[int(c)]}{'s' * (n > 1)}, "
                    # s >> image 1/36 /home/kawano/etrobocon2023-camera-system/src/detect_fig/verification_data/image1.png: 640x640 1 front,

                # Write results
                # バウンディングボックスの座標(xyxy：[x_min, y_min, x_max, y_max] 形式)、信頼度(conf)、クラスID(cls)
                for *xyxy, conf, cls in reversed(det):
                    if save_img:
                        c = int(cls)  # クラスid

                        label = f'{labels[c]} {conf:.2f}'
                        # label >> front 0.94
                        #
                        """
                        annotator.box_label():画像にバウンディングボックスとラベルを追加
                        colors():検出されたクラスのインデックスに基づいて、一意の色を生成。
                                 True パラメータは、色をランダムに選択することを指示。
                                 異なるクラスは異なる色で表示されます。
                        """
                        annotator.box_label(xyxy, label, color=colors(c, True))

            # 検出結果を含む画像を保存
            im0 = annotator.result()
            if save_img:
                cv2.imwrite(save_path, im0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str,
                        default='yolov5s.pt', help='model path or triton URL')
    parser.add_argument('--source', type=str, default=# parser.add_argument('--source', type=str, default=ROOT /
                        'data/images', help='file/dir/URL/glob/screen/0(webcam)')
    parser.add_argument('--data', type=str, default=# parser.add_argument('--data', type=str, default=ROOT /
                        'data/coco128.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+',
                        type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float,
                        default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float,
                        default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000,
                        help='maximum detections per image')
    parser.add_argument('--device', default='cpu',
                        help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--nosave', action='store_true',
                        help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int,
                        help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true',
                        help='class-agnostic NMS')
    parser.add_argument('--project', default=# parser.add_argument('--project', default=ROOT /
                        'runs/detect', help='save results to project/name')
    parser.add_argument('--line-thickness', default=3,
                        type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--vid-stride', type=int, default=1,
                        help='video frame-rate stride')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1

    run(**vars(opt))

    print('完了!!')
