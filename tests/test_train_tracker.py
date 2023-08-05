"""TrainTrackerクラスのテストコードを記述するモジュール.

@author: miyashita64
"""
from src.train_tracker import TrainTracker
from unittest import mock


class TestTrainTracker:
    @mock.patch('cv2.VideoWriter')
    @mock.patch("cv2.waitKey", side_effect=[ord("q"), ord("q"), ord("q")])  # キーボード入力をシミュレート
    def test_calibrate(self, mock_wait_key, mock_video_writer):
        mock_video_writer.return_value = mock.Mock()    # 動画ファイルを生成しない
        tt = TrainTracker(2)
        tt.calibrate()

    @mock.patch('cv2.VideoWriter')
    @mock.patch("cv2.waitKey", side_effect=[ord("q"), ord("q"), ord("q")])  # キーボード入力をシミュレート
    def test_observe(self, mock_wait_key, mock_video_writer):
        mock_video_writer.return_value = mock.Mock()    # 動画ファイルを生成しない
        tt = TrainTracker(2)
        tt.observe()