import cv2

class CameraInterface:
    """カメラを制御するクラス"""

    def __init__(self, camera_id: int) -> None:
        """コンストラクタ.

        Args:
            camera_id (int): カメラID
        """
        self.camera = cv2.VideoCapture(camera_id)
        self.movie_dir = "../video/"

    def recording(self) -> None:
        """動画を撮影する."""
        # 動画のコーデック(変換器)
        codec = cv2.VideoWriter_fourcc(*'XVID')
        # 出力ファイル名、コーデック、フレームレート、解像度
        video = cv2.VideoWriter(f"{self.movie_dir}latest.avi", codec, 20.0, (640, 480))

        # フレームを取得して動画に書き込む
        while True:
            # フレームを取得
            success, frame = self.camera.read()  

            if success:
                # フレームを動画に書き込む
                video.write(frame)

                # フレームを表示
                cv2.imshow('Frame', frame)

                # 'q'キーでループを終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

        # リソースを解放
        self.camera.release()  # カメラデバイスを解放
        video.release()  # 動画ファイルを解放
        cv2.destroyAllWindows()  # ウィンドウを閉じる

if __name__ == '__main__':
    ci = CameraInterface(0)
    ci.recording()
