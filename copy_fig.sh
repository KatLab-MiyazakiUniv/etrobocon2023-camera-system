#!/bin/bash

# 引数は2つ
# 第1引数が接続先IPアドレス、第2引数がコピー元画像ファイル名

# リモートマシンのユーザ名と接続先IPアドレス
# 第1引数をREMOTE_IPに格納する
REMOTE_IP="$1"
REMOTE_USER="et2023"
REMOTE_PASS=

# コピー元画像ファイル
# 第2引数をIMAGE_NAMEに格納
IMAGE_NAME="$2"

# リモート上のコピー元のパス
REMOTE_DIRECTORY="~/work/RasPike/sdk/workspace/etrobocon2023/rear_camera_py/image_data/"

# ローカル上のコピー先のパス
LOCAL_DIRECTORY="./fig_image/"

# SSH経由で画像をコピー
# scp "$REMOTE_USER@$REMOTE_IP:$REMOTE_DIRECTORY$IMAGE_NAME" "$LOCAL_DIRECTORY"

# FTP経由で画像をコピー
ftp -n ${REMOTE_IP} <<END_SCRIPT
quote USER ${REMOTE_USER}
quote PASS ${REMOTE_PASS}
get ${REMOTE_DIRECTORY}${IMAGE_NAME} ${LOCAL_DIRECTORY}${IMAGE_NAME}
quit
END_SCRIPT

# スクリプトの終了
exit 0