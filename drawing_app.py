import tkinter as tk
import math
from shape_selector import setup_shape_selection

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shape Drag Preview App")

        self.toolbar = tk.Frame(root, pady=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.pencil_button = tk.Button(self.toolbar, text="✏️ Pencil", command=self.use_pencil)
        self.pencil_button.pack(side=tk.LEFT, padx=5)

        self._add_rgb_inputs()

        self.eraser_button = tk.Button(self.toolbar, text="🧽 Eraser", command=self.use_eraser)
        self.eraser_button.pack(side=tk.LEFT, padx=5)

        self.fill_button = tk.Button(self.toolbar, text="🪣 Fill", command=self.use_fill)
        self.fill_button.pack(side=tk.LEFT, padx=5)

        self.shape_button = tk.Button(self.toolbar, text="🔄 Shape: Circle", command=self.update_shape_button)
        self.shape_button.pack(side=tk.LEFT, padx=5)

        self.up_button = tk.Button(self.toolbar, text="🔼 Up", command=self.add_shape_sides)
        self.up_button.pack(side=tk.LEFT, padx=5)

        self.down_button = tk.Button(self.toolbar, text="🔽 Down", command=self.remove_shape_sides)
        self.down_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack()

        setup_shape_selection(self.canvas, root, self.toolbar)

        self.shapes = ["Circle", "Triangle", "Square"]
        self.shape_index = 0
        self.custom_mode = False
        self.current_shape_sides = 0
        self.reverse_direction = False
        self.preview_shape = None
        self.start_x = self.start_y = None
        self.last_x = self.last_y = None
        self.current_color = "black"
        self.eraser_mode = False
        self.fill_mode = False
        self.shape_mode = True
        self.is_dragging = False
        self.undo_stack = []

        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<Button-3>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_drag)
        self.canvas.bind("<B3-Motion>", self.mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind("<ButtonRelease-3>", self.mouse_up)
        root.bind("<Up>", self.keyboard_up)
        root.bind("<Down>", self.keyboard_down)
        root.bind("<Control-z>", self.undo)

    def _add_rgb_inputs(self):
        self.r_entry = self._add_color_input("R:")
        self.g_entry = self._add_color_input("G:")
        self.b_entry = self._add_color_input("B:")
        self.color_button = tk.Button(self.toolbar, text="🎨 Set Color", command=self.set_color_from_rgb)
        self.color_button.pack(side=tk.LEFT, padx=5)

    def _add_color_input(self, label):
        tk.Label(self.toolbar, text=label).pack(side=tk.LEFT)
        entry = tk.Entry(self.toolbar, width=4)
        entry.insert(0, "0")
        entry.pack(side=tk.LEFT)
        return entry

    def get_shape_name(self):
        if self.custom_mode:
            return f"{3 + self.current_shape_sides}-gon"
        else:
            return self.shapes[self.shape_index]

    def update_shape_button(self):
        self.shape_button.config(text=f"🔄 Shape: {self.get_shape_name()}")

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
            print("Invalid RGB values")

    def use_pencil(self):
        if self.canvas.selection_mode: self.canvas.disable_selection_mode()
        self.eraser_mode = False
        self.fill_mode = False
        self.shape_mode = False

    def use_eraser(self):
        if self.canvas.selection_mode: self.canvas.disable_selection_mode()
        self.eraser_mode = True
        self.fill_mode = False
        self.shape_mode = False

    def use_fill(self):
        if self.canvas.selection_mode: self.canvas.disable_selection_mode()
        self.fill_mode = True
        self.eraser_mode = False
        self.shape_mode = False

    def add_shape_sides(self, event=None):
        if not self.custom_mode:
            if self.shape_index < 2:
                self.shape_index += 1
            else:
                self.custom_mode = True
                self.current_shape_sides = 0
        else:
            self.current_shape_sides += 1
        self.update_shape_button()
        if self.is_dragging:
            self.refresh_preview()

    def remove_shape_sides(self, event=None):
        if self.custom_mode:
            if self.current_shape_sides > 0:
                self.current_shape_sides -= 1
            else:
                self.custom_mode = False
                self.shape_index = 2
        elif self.shape_index > 0:
            self.shape_index -= 1
        else:
            return
        self.update_shape_button()
        if self.is_dragging:
            self.refresh_preview()

    def keyboard_up(self, event):
        if self.shape_mode and self.is_dragging:
            self.add_shape_sides()

    def keyboard_down(self, event):
        if self.shape_mode and self.is_dragging:
            self.remove_shape_sides()

    def undo(self, event=None):
        if self.undo_stack:
            item = self.undo_stack.pop()
            self.canvas.delete(item)

    def mouse_down(self, event):
        self.start_x = self.last_x = event.x
        self.start_y = self.last_y = event.y
        self.reverse_direction = (event.num == 3)
        self.is_dragging = True
        if self.fill_mode:
            self.canvas.create_rectangle(0, 0, 800, 600, fill=self.current_color, outline="")

    def mouse_drag(self, event):
        self.last_x, self.last_y = event.x, event.y
        if self.shape_mode:
            self.refresh_preview()

    def mouse_up(self, event):
        if self.shape_mode and self.preview_shape:
            self.canvas.delete(self.preview_shape)
            shape_id = self.draw_shape(self.start_x, self.start_y, event.x, event.y)
            if shape_id:
                self.canvas.tag_new_item(shape_id)
                self.undo_stack.append(shape_id)
            self.preview_shape = None
        self.last_x = self.last_y = None
        self.is_dragging = False

    def refresh_preview(self):
        if self.preview_shape:
            self.canvas.delete(self.preview_shape)
        self.preview_shape = self.draw_shape(self.start_x, self.start_y, self.last_x, self.last_y, preview=True)

    def draw_shape(self, x1, y1, x2, y2, preview=False):
        shape = self.get_shape_name()
        color = self.current_color
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if "gon" in shape:
            sides = int(shape.split("-")[0])
            angle = 2 * math.pi / sides
            radius = min(width, height) / 2
            points = []
            for i in range(sides):
                theta = -i * angle if self.reverse_direction else i * angle
                px = center_x + radius * math.cos(theta)
                py = center_y + radius * math.sin(theta)
                points.extend([px, py])
            return self.canvas.create_polygon(points, fill=color if not preview else "", outline=color, dash=(4, 2) if preview else None)

        if shape == "Circle":
            return self.canvas.create_oval(x1, y1, x2, y2, fill=color if not preview else "", outline=color, dash=(4, 2) if preview else None)
        elif shape == "Triangle":
            points = [center_x, y1, x2, y2, x1, y2] if self.reverse_direction else [center_x, y1, x1, y2, x2, y2]
            return self.canvas.create_polygon(points, fill=color if not preview else "", outline=color, dash=(4, 2) if preview else None)
        elif shape == "Square":
            return self.canvas.create_rectangle(x2, y2, x1, y1, fill=color if not preview else "", outline=color, dash=(4, 2) if preview else None) if self.reverse_direction else self.canvas.create_rectangle(x1, y1, x2, y2, fill=color if not preview else "", outline=color, dash=(4, 2) if preview else None)


    def paint(self, event):
        x, y = event.x, event.y
        color = self.canvas["bg"] if self.eraser_mode else self.current_color
        width = 10 if self.eraser_mode else 2
        if self.last_x is not None and self.last_y is not None:
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=color, width=width)
        self.last_x, self.last_y = x, y

    def reset(self, event):
        self.last_x = self.last_y = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
