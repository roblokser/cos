import os
import sys
import ctypes
import tkinter as tk
from PIL import Image, ImageTk

CODE = "181188"

# (файл, секунд показа, макс. ширина, макс. высота, центр по высоте) - доли экрана
# последняя картинка остаётся до закрытия
SLIDES = [
    ("furry.jpg", 0.3, 1.0, 1.0, 0.50),
    ("scythe.png", 0.3, 1.0, 1.0, 0.50),
    ("eye.png", None, 0.60, 0.50, 0.40),   # глаз чуть выше середины
]

mci = ctypes.windll.winmm.mciSendStringW
opened = []


def res(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def mci_status(alias):
    buf = ctypes.create_unicode_buffer(64)
    mci(f"status {alias} mode", buf, 64, None)
    return buf.value


def play_once(filename, then):
    # проигрывает звук один раз, потом вызывает then()
    alias = "snd_" + filename.split(".")[0]
    mci(f'open "{res(filename)}" type mpegvideo alias {alias}', None, 0, None)
    mci(f"play {alias}", None, 0, None)
    opened.append(alias)

    def check():
        if mci_status(alias) == "playing":
            root.after(100, check)
        else:
            mci(f"close {alias}", None, 0, None)
            then()

    root.after(100, check)


def start_music():
    # музыка по кругу, пока программу не закроют
    mci(f'open "{res("music.mp3")}" type mpegvideo alias music', None, 0, None)
    mci("play music repeat", None, 0, None)
    opened.append("music")


def close(_event=None):
    for alias in opened:
        mci(f"stop {alias}", None, 0, None)
        mci(f"close {alias}", None, 0, None)
    root.destroy()


def load_slide(name, wf, hf):
    img = Image.open(res(name)).convert("RGB")
    bg = "#%02x%02x%02x" % img.getpixel((0, 0))
    scale = min(sw * wf / img.width, sh * hf / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return ImageTk.PhotoImage(img), bg


def build_input():
    # длинный ромб с полем для кода
    cx, cy = sw // 2, int(sh * 0.80)
    w, h = int(sw * 0.50), int(sh * 0.14)
    canvas.create_polygon(
        cx - w // 2, cy, cx, cy - h // 2, cx + w // 2, cy, cx, cy + h // 2,
        outline="white", fill="black", width=3,
    )
    entry = tk.Entry(
        root, font=("Consolas", 28), justify="center", bg="black", fg="white",
        insertbackground="white", bd=0, highlightthickness=0,
    )
    canvas.create_window(cx, cy, window=entry, width=int(w * 0.40), height=46)
    error_id = canvas.create_text(
        cx, cy + h // 2 + 40, text="", fill="red", font=("Consolas", 32, "bold")
    )

    def clear_error():
        canvas.itemconfigure(error_id, text="")

    def check_code(_event=None):
        if entry.get().strip() == CODE:
            close()
        else:
            canvas.itemconfigure(error_id, text="error")
            entry.delete(0, "end")
            root.after(1500, clear_error)

    entry.bind("<Return>", check_code)
    canvas.bind("<Button-1>", lambda e: entry.focus_force())
    root.after(200, entry.focus_force)


def show(i):
    photo, bg = photos[i]
    canvas.delete("slide")
    canvas.configure(bg=bg)
    root.configure(bg=bg)
    canvas.create_image(sw // 2, int(sh * SLIDES[i][4]), image=photo, tags="slide")
    if i + 1 < len(SLIDES):
        root.after(int(SLIDES[i][1] * 1000), show, i + 1)
    else:
        build_input()


root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.protocol("WM_DELETE_WINDOW", close)   # Alt+F4 тоже закрывает

sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
canvas = tk.Canvas(root, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)
photos = [load_slide(n, wf, hf) for n, _, wf, hf, _ in SLIDES]

# glitch -> крик -> музыка по кругу
play_once("glitch.mp3", lambda: play_once("scream.mp3", start_music))
show(0)
root.mainloop()
