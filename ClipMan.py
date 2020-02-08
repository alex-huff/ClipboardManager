import pickle
import traceback

import win32clipboard
from pynput import keyboard


class ClipMan(keyboard.Listener):
    def __init__(self, file):
        super().__init__(
            on_press=self.press,
            on_release=self.release
        )

        self.file = file
        self.bindings = {
            (
                keyboard.Key.ctrl_l,
                keyboard.Key.shift,
                keyboard.KeyCode.from_char('z'),
            ): self.copy,
            (
                keyboard.Key.ctrl_l,
                keyboard.Key.shift,
                keyboard.KeyCode.from_char('x'),
            ): self.paste
        }

        self.pressed = []

        try:
            with open(self.file, 'rb') as r_file:
                self.clippings = pickle.load(r_file)
        except FileNotFoundError:
            self.clippings = ['' for _ in range(10)]

        self.start()
        self.join()

    def press(self, key):
        if key not in self.pressed:
            self.pressed.append(key)
            self.handle_keys()

    def release(self, key):
        if key in self.pressed:
            self.pressed.remove(key)

    def handle_keys(self):
        for i in range(len(self.pressed)):
            if isinstance(self.pressed[i], keyboard.KeyCode) and self.pressed[i].char.isnumeric():
                args = self.pressed[i:]
                binding = tuple(self.pressed[:i])

                if binding in self.bindings:
                    # noinspection PyTypeChecker
                    self.bindings[binding](*args)

                break

    def copy(self, *args):
        win32clipboard.OpenClipboard()

        try:
            self.clippings[int(args[0].char)] = win32clipboard.GetClipboardData()
        finally:
            win32clipboard.CloseClipboard()

        pickle.dump(self.clippings, open(self.file, 'wb'))

    def paste(self, *args):
        win32clipboard.OpenClipboard()

        try:
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, self.clippings[int(args[0].char)])
        finally:
            win32clipboard.CloseClipboard()


try:
    ClipMan('clippings.ser')
except Exception as e:
    with open('error.log', 'a') as w_file:
        w_file.write(traceback.format_exc())
