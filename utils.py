import os
import json
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal, Qt


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

SETTINGS_PATH = "data/settings.json"


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"prefer_sharps": False}


def save_settings(prefer_sharps: bool):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump({"prefer_sharps": prefer_sharps}, f)


def set_prefer_sharps(value: bool):
    from note import NoteNames
    NoteNames.PREFER_SHARPS = value
    save_settings(value)


#-----------------------#
#       GUI Assets      #
#-----------------------#
class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()