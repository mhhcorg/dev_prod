import os
from pathlib import Path
from time import sleep

""" 2024-09-17 """
class DisplayLine:
    def __init__(self, message: str = "", display_width: int = 120):
        self.display_width = display_width
        self.message = str(message + " " * display_width)[:display_width]
        self.display(self.message)

    def display(self, message: str, position: int = 0, width: int = 0):
        if width == 0:
            width = self.display_width
        message = str(message + " " * width)[:width]
        self.message = str(
            self.message[0:position]
            + message
            + self.message[(len(message) + position) :]
        )[: self.display_width]
        print("\r" + self.message, end="\r")

    def progress_bar(self, message: str, progress: int = 0, max: int = 120):
        self.display(message + " " * 2, 0, len(message) + 2)
        self.display("_" * max, len(message) + 2, max)
        self.display("|" * progress, len(message) + 2, progress)


if __name__ == "__main__":
    show = DisplayLine()
    show.display('Starting Something')
    sleep(2)
    show.progress_bar('Progress',10,100)
    sleep(2)
    show.progress_bar('Progress',20,100)