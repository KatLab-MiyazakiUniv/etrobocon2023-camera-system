"""mainモジュール.

プロジェクトルートで、以下のコマンドを実行すると最初に呼び出されるファイル
> poetry run python camera_system

必要最低限のコードのみを記述するようにする
@author: kawanoichi
"""

import argparse
import camera_system

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Camera System settings.')

    args = parser.parse_args()

    cs = camera_system.CameraSystem()
    result = cs.start()
    print("result: ", result)
