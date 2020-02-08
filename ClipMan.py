import pickle
import traceback

import win32clipboard
from googletrans import Translator
from pynput import keyboard


class ClipMan(keyboard.Listener):
    def __init__(self, file):
        super().__init__(
            on_press=self.press,
            on_release=self.release
        )

        self.numeric = range(48, 58)
        self.file = file
        self.translator = Translator()
        self.bindings = {
            (162, 160, 90): self.copy,
            (162, 160, 88): self.paste,
            (162, 160, 84): self.translate
        }
        self.pressed = []

        try:
            with open(self.file, 'rb') as r_file:
                self.clippings = pickle.load(r_file)
        except FileNotFoundError:
            self.clippings = ['' for _ in range(10)]

        self.start()
        self.join()

    @staticmethod
    def handle_exc():
        with open('error.log', 'a') as w_file:
            w_file.write(traceback.format_exc())

    @staticmethod
    def open_cb():
        try:
            win32clipboard.OpenClipboard()
            return True
        except Exception:
            ClipMan.handle_exc()

            return False

    @staticmethod
    def code(key):
        if isinstance(key, keyboard.KeyCode):
            return key.vk
        if isinstance(key, keyboard.Key):
            return key.value.vk

        return -1

    def press(self, key):
        code = ClipMan.code(key)

        if code < 0:
            return

        if code not in self.pressed:
            self.pressed.append(code)
            self.handle_keys()

    def release(self, key):
        code = ClipMan.code(key)

        if code < 0:
            return

        if code in self.pressed:
            self.pressed.remove(code)

    def handle_keys(self):
        split_index = len(self.pressed)

        for i in range(len(self.pressed)):
            if self.pressed[i] in self.numeric:
                split_index = i

                break

        args = [code - self.numeric.start for code in self.pressed[split_index:]]
        binding: tuple = tuple(self.pressed[:split_index])

        if binding in self.bindings:
            self.bindings[binding](*args)

    def copy(self, *args):
        if len(args) == 0 or not ClipMan.open_cb():
            return

        try:
            self.clippings[args[0]] = win32clipboard.GetClipboardData()
        except Exception:
            ClipMan.handle_exc()

        win32clipboard.CloseClipboard()
        pickle.dump(self.clippings, open(self.file, 'wb'))

    def paste(self, *args):
        if len(args) == 0 or not ClipMan.open_cb():
            return

        try:
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, self.clippings[args[0]])
        except Exception:
            ClipMan.handle_exc()

        win32clipboard.CloseClipboard()

    # noinspection PyUnusedLocal
    def translate(self, *args):
        if not ClipMan.open_cb():
            return

        try:
            translation = self.translator.translate(
                win32clipboard.GetClipboardData(),
                src='en',
                dest='es'
            ).text

            win32clipboard.SetClipboardData(
                win32clipboard.CF_UNICODETEXT,
                translation
            )
        except Exception:
            ClipMan.handle_exc()

        win32clipboard.CloseClipboard()


try:
    ClipMan('clippings.ser')
except Exception:
    ClipMan.handle_exc()
