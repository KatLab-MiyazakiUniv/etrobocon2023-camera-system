#!/bin/bash

# テスト用の競技システムのWebサーバを起動する
#  使用条件
#   - テスト用の競技システムが起動している
#   - テスト用の競技システムとLANケーブルで接続している

RUN_SERVER_COMMAND="cd /opt/compesys && sudo npm run start"
ssh et2023@official-system "${RUN_SERVER_COMMAND}"