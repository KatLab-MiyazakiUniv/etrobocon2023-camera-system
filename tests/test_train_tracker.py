"""TrainTrackerクラスのテストコードを記述するモジュール.

@author: miyashita64
"""
from unittest import mock
from src.train_tracker import TrainTracker
from src.camera_interface import CameraInterface


@mock.patch("cv2.VideoWriter", mock.Mock())
@mock.patch("cv2.namedWindow", mock.Mock())
@mock.patch("cv2.imshow", mock.Mock())
@mock.patch("cv2.cvtColor", mock.Mock())
@mock.patch("cv2.rectangle", mock.Mock())
@mock.patch("cv2.setMouseCallback", mock.Mock())
@mock.patch("src.train_tracker.CameraInterface.get_frame",
            return_value=(True, mock.Mock()))
@mock.patch("src.train_tracker.CameraInterface.start_record",
            return_value=(mock.Mock(), mock.Mock()))
@mock.patch("src.train_tracker.CameraInterface.end_record", mock.Mock())
class TestTrainTracker:
    @mock.patch("cv2.waitKey",
                side_effect=[ord("0"), ord("0"), ord("0"),
                             ord("q"), ord("q"), ord("q")])
    def test_calibrate(self, mock_get_frame, *mocks):
        tt = TrainTracker()
        tt.calibrate()

    @mock.patch("cv2.waitKey", side_effect=[ord("0"), ord("0"), ord("0"),
                                            ord("q"), ord("q"), ord("q")])
    @mock.patch("src.train_tracker.TrainTracker.detect_train",
                return_value=(mock.Mock(), [(20, 1), (80, 50)]))
    @mock.patch("src.train_tracker.OfficialInterface.set_train_pwm",
                mock.Mock())
    def test_observe(self, mock_detect_train, *mocks):
        tt = TrainTracker()
        tt.calibrate()
        tt.observe_rect_points = [(10, 40), (90, 60)]
        tt.observe()
