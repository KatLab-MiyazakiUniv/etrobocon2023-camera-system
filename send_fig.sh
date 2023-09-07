#!/bin/bash

# 引数は2つ
# 第1引数が接続先IPアドレス、第2引数が送信元画像ファイル名

# リモートマシンのユーザ名と接続先IPアドレス
# 第1引数をREMOTE_IPに格納する
REMOTE_USER="et2023"
REMOTE_IP="$1"

# 送信元画像ファイル
# 第2引数をIMAGE_NAMEに格納
IMAGE_NAME="$2"

# リモート上のコピー元のパス
REMOTE_DIRECTORY="~/work/RasPike/sdk/workspace/etrobocon2023/rear_camera_py/image_data/"

# ローカル上のコピー先のパス
LOCAL_DIRECTORY="./fig_image/"

# SSH経由で画像を転送
scp "$REMOTE_USER@$REMOTE_IP:$REMOTE_DIRECTORY$IMAGE_NAME" "$LOCAL_DIRECTORY"

# スクリプトの終了
exit 0