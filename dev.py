from pathlib import Path
from time import sleep

from doitlive.screencast import ScreenCaster


PATH = Path("videos/dev.mp4")


def emulate_script(seconds):
    for i in range(seconds):
        print(i)
        sleep(1.0)

    print("Done")



with ScreenCaster(PATH) as screencaster:
    emulate_script(3)
