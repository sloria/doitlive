from pathlib import Path
from typing import Self


class ScreenCaster:
    def __init__(self, width: int = 600, height: int = 800) -> None:
        self.width = width
        self.height = height

    def __enter__(self) -> Self:
        print("Start recording...")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print("Stop recording...")

