"""mainモジュール.

プロジェクトルートで、以下のコマンドを実行すると最初に呼び出されるファイル
> poetry run python camera_system

必要最低限のコードのみを記述するようにする
@author: kawanoichi
"""

import argparse
import camera_system
from train_tracker import TrainTracker

if __name__ == '__main__':
    tt = TrainTracker(0)
    tt.observe()
    # parser = argparse.ArgumentParser(description='Camera System settings.')

    # args = parser.parse_args()

    # cs = camera_system.CameraSystem()
    # cs.start()
