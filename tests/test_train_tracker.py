"""TrainTrackerクラスのテストコードを記述するモジュール.

@author: miyashita64
"""
from src.train_tracker import TrainTracker
from unittest import mock


class TestTrainTracker:
    @mock.patch('cv2.VideoWriter')
    @mock.patch("cv2.namedWindow")
    @mock.patch("cv2.setMouseCallback")
    @mock.patch("cv2.waitKey", side_effect=[ord("q"), ord("q"), ord("q")])
    @mock.patch("src.train_tracker.CameraInterface.end_record")
    def test_calibrate(self, mock_end_record, mock_wait_key,
                       mock_set_mouse_callback,
                       mock_named_window, mock_video_writer):
        mock_end_record.return_value = None
        mock_set_mouse_callback.return_value = None
        mock_named_window.return_value = None
        mock_video_writer.return_value = mock.Mock()    # 動画ファイルを生成しない
        tt = TrainTracker(2)
        tt.calibrate()

    @mock.patch('cv2.VideoWriter')
    @mock.patch("cv2.namedWindow")
    @mock.patch("cv2.setMouseCallback")
    @mock.patch("cv2.waitKey", side_effect=[ord("q"), ord("q"), ord("q")])
    @mock.patch("src.train_tracker.CameraInterface.end_record")
    def test_observe(self, mock_end_record, mock_wait_key,
                     mock_set_mouse_callback,
                     mock_named_window, mock_video_writer):
        mock_end_record.return_value = None
        mock_set_mouse_callback.return_value = None
        mock_named_window.return_value = None
        mock_video_writer.return_value = mock.Mock()    # 動画ファイルを生成しない
        tt = TrainTracker(2)
        tt.observe()
