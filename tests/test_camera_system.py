from src.camera_system import CameraSystem


def test_camera_system_start():
    cs = CameraSystem()
    assert cs.start() is None
