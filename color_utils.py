
import tkinter as tk
from tkinter import colorchooser

def rgb_to_hex(r, g, b):
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError("RGB values must be between 0 and 255")
    return f'#{r:02x}{g:02x}{b:02x}'

def set_color_from_rgb(app):
    try:
        r = int(app.r_entry.get())
        g = int(app.g_entry.get())
        b = int(app.b_entry.get())
        app.current_color = rgb_to_hex(r, g, b)
        app.eraser_mode = False
        app.fill_mode = False
    except ValueError:
        print("Invalid RGB values")

def pick_color(app):
    color_tuple = colorchooser.askcolor(title="Choose color")
    if color_tuple and color_tuple[0] and color_tuple[1]:
        r, g, b = map(int, color_tuple[0])
        app.r_entry.delete(0, tk.END)
        app.r_entry.insert(0, str(r))
        app.g_entry.delete(0, tk.END)
        app.g_entry.insert(0, str(g))
        app.b_entry.delete(0, tk.END)
        app.b_entry.insert(0, str(b))
        app.current_color = color_tuple[1]
        app.eraser_mode = False
        app.fill_mode = False

def add_color_input(parent, label):
    tk.Label(parent, text=label).pack(side=tk.LEFT)
    entry = tk.Entry(parent, width=4)
    entry.insert(0, "0")
    entry.pack(side=tk.LEFT)
    return entry