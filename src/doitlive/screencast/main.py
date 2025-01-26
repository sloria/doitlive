import threading
import time
from pathlib import Path
from typing import Self

import cv2
import mss
import numpy as np


class ScreenCaster:
    def __init__(self, filepath: Path, width: int = 600, height: int = 800) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        self.filepath = filepath
        self.width = width
        self.height = height

        self._fps = 20
        self._codec = cv2.VideoWriter_fourcc(*"XVID")
        self._buffer = None
        self._is_recording = False
        self._recoding_thread = None

    def record(self) -> None:
        monitor = {"top": 0, "left": 0, "width": self.width, "height": self.height}
        with mss.mss() as sct:
            frame_duration = 1 / self._fps

            while self._is_recording:
                start_time = time.time()

                img = sct.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._buffer.write(frame)

                elapsed_time = time.time() - start_time
                time_to_wait = frame_duration - elapsed_time
                if time_to_wait > 0:
                    time.sleep(time_to_wait)

    def __enter__(self) -> Self:
        print("Start recording...")
        self._buffer = cv2.VideoWriter(
            str(self.filepath), self._codec, self._fps, (self.width, self.height)
        )
        self._is_recording = True
        self._recoding_thread = threading.Thread(target=self.record)
        self._recoding_thread.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print("Stop recording...")
        self._is_recording = False
        if self._recoding_thread.is_alive():
            self._recoding_thread.join()

        self._buffer.release()
