#!/bin/bash

# テスト用の競技システムのWebサーバを起動する
#  使用条件
#   - テスト用の競技システムが起動している
#   - テスト用の競技システムとLANケーブルで接続している

SERVE_COMMAND="cd /opt/compesys && sudo npm run start"
ssh et2023@official-system "${SERVE_COMMAND}" 