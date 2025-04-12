import tkinter as tk


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Drawing App")

        # Toolbar
        self.toolbar = tk.Frame(root, pady=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Pencil
        self.pencil_button = tk.Button(self.toolbar, text="✏️ Pencil", command=self.use_pencil)
        self.pencil_button.pack(side=tk.LEFT, padx=5)

        # RGB Inputs
        self.r_label = tk.Label(self.toolbar, text="R:")
        self.r_label.pack(side=tk.LEFT)
        self.r_entry = tk.Entry(self.toolbar, width=4)
        self.r_entry.insert(0, "0")
        self.r_entry.pack(side=tk.LEFT)

        self.g_label = tk.Label(self.toolbar, text="G:")
        self.g_label.pack(side=tk.LEFT)
        self.g_entry = tk.Entry(self.toolbar, width=4)
        self.g_entry.insert(0, "0")
        self.g_entry.pack(side=tk.LEFT)

        self.b_label = tk.Label(self.toolbar, text="B:")
        self.b_label.pack(side=tk.LEFT)
        self.b_entry = tk.Entry(self.toolbar, width=4)
        self.b_entry.insert(0, "0")
        self.b_entry.pack(side=tk.LEFT)

        self.color_button = tk.Button(self.toolbar, text="🎨 Set Color", command=self.set_color_from_rgb)
        self.color_button.pack(side=tk.LEFT, padx=5)

        # Eraser
        self.eraser_button = tk.Button(self.toolbar, text="🧽 Eraser", command=self.use_eraser)
        self.eraser_button.pack(side=tk.LEFT, padx=5)

        # Fill Bucket
        self.fill_button = tk.Button(self.toolbar, text="🪣 Fill", command=self.use_fill)
        self.fill_button.pack(side=tk.LEFT, padx=5)

        # Canvas
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack()

        self.last_x, self.last_y = None, None
        self.current_color = "black"
        self.eraser_mode = False
        self.fill_mode = False

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.canvas.bind("<Button-1>", self.handle_click)

    def use_pencil(self):
        self.eraser_mode = False
        self.fill_mode = False
        self.current_color = "black"

    def set_color_from_rgb(self):
        try:
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())
            if all(0 <= val <= 255 for val in (r, g, b)):
                self.current_color = f'#{r:02x}{g:02x}{b:02x}'
                self.eraser_mode = False
                self.fill_mode = False
        except ValueError:
            print("Invalid RGB values. Use 0–255.")

    def use_eraser(self):
        self.eraser_mode = True
        self.fill_mode = False

    def use_fill(self):
        self.fill_mode = True
        self.eraser_mode = False

    def handle_click(self, event):
        if self.fill_mode:
            self.canvas.create_rectangle(0, 0, 800, 600, fill=self.current_color, outline="")

    def paint(self, event):
        if self.fill_mode:
            return  # Don't paint in fill mode

        x, y = event.x, event.y
        color = self.canvas["bg"] if self.eraser_mode else self.current_color
        width = 10 if self.eraser_mode else 2

        if self.last_x is not None and self.last_y is not None:
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=color, width=width)

        self.last_x, self.last_y = x, y

    def reset(self, event):
        self.last_x, self.last_y = None, None


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
