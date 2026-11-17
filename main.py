import os
import sys
import ctypes
import tkinter as tk
from PIL import Image, ImageTk

# Порядок картинок и сколько секунд показывать каждую (последняя остаётся до закрытия)
SLIDES = [
    ("furry.jpg", 2.0),
    ("scythe.png", 2.0),
    ("eye.png", None),
]


def res(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)

mci = ctypes.windll.winmm.mciSendStringW


def mci_status(alias):
    buf = ctypes.create_unicode_buffer(64)
    mci(f"status {alias} mode", buf, 64, None)
    return buf.value


def start_glitch():
    # звук в самом начале (один раз)
    mci(f'open "{res("glitch.mp3")}" type mpegvideo alias glitch', None, 0, None)
    mci("play glitch", None, 0, None)
    root.after(100, wait_glitch)


def wait_glitch():
    # когда звук закончился - музыка по кругу, пока программу не закроют
    if mci_status("glitch") == "playing":
        root.after(100, wait_glitch)
        return
    mci("close glitch", None, 0, None)
    mci(f'open "{res("music.mp3")}" type mpegvideo alias music', None, 0, None)
    mci("play music repeat", None, 0, None)


def close(_event=None):
    for alias in ("glitch", "music"):
        mci(f"stop {alias}", None, 0, None)
        mci(f"close {alias}", None, 0, None)
    root.destroy()


def load_slide(name):
    img = Image.open(res(name)).convert("RGB")
    bg = "#%02x%02x%02x" % img.getpixel((0, 0))   # фон окна под цвет картинки
    scale = min(sw / img.width, sh / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return ImageTk.PhotoImage(img), bg


def show(i):
    photo, bg = photos[i]
    root.configure(bg=bg)
    label.configure(image=photo, bg=bg)
    delay = SLIDES[i][1]
    if delay is not None and i + 1 < len(SLIDES):
        root.after(int(delay * 1000), show, i + 1)


root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.bind("<Escape>", close)          # Esc закрывает программу
root.protocol("WM_DELETE_WINDOW", close)

sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
photos = [load_slide(name) for name, _ in SLIDES]
label = tk.Label(root, bd=0)
label.pack(expand=True, fill="both")

start_glitch()
show(0)
root.mainloop()
