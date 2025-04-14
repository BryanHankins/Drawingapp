import tkinter as tk
from tkinter import colorchooser
from shape_selector import setup_shape_selection
from shapes import Circle, Triangle, Square, PolygonShape

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shape Drag Preview App")

        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_canvas)
        file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        self.toolbar = tk.Frame(root, pady=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        tools_frame = tk.LabelFrame(self.toolbar, text="Tools", padx=5, pady=5)
        tools_frame.pack(side=tk.LEFT, padx=5)

        self.brush_size_var = tk.IntVar(value=2)
        tk.Label(tools_frame, text="Size:").pack(side=tk.LEFT)
        tk.OptionMenu(tools_frame, self.brush_size_var, 1, 2, 4, 8, 10).pack(side=tk.LEFT)

        self.pencil_button = tk.Button(tools_frame, text="✏️ Pencil", command=self.use_pencil)
        self.pencil_button.pack(side=tk.LEFT, padx=2)

        self.eraser_button = tk.Button(tools_frame, text="🧽 Eraser", command=self.use_eraser)
        self.eraser_button.pack(side=tk.LEFT, padx=2)

        self.fill_button = tk.Button(tools_frame, text="🪣 Fill", command=self.use_fill)
        self.fill_button.pack(side=tk.LEFT, padx=2)

        shapes_frame = tk.LabelFrame(self.toolbar, text="Shapes", padx=5, pady=5)
        shapes_frame.pack(side=tk.LEFT, padx=5)

        self.shape_button = tk.Button(shapes_frame, text="🔄 Shape: Circle", command=self.update_shape_button)
        self.shape_button.pack(side=tk.LEFT, padx=2)

        self.up_button = tk.Button(shapes_frame, text="🔼 Up", command=self.add_shape_sides)
        self.up_button.pack(side=tk.LEFT, padx=2)

        self.down_button = tk.Button(shapes_frame, text="🔽 Down", command=self.remove_shape_sides)
        self.down_button.pack(side=tk.LEFT, padx=2)

        color_frame = tk.LabelFrame(self.toolbar, text="Colors", padx=5, pady=5)
        color_frame.pack(side=tk.LEFT, padx=5)

        self.r_entry = self._add_color_input(color_frame, "R:")
        self.g_entry = self._add_color_input(color_frame, "G:")
        self.b_entry = self._add_color_input(color_frame, "B:")

        tk.Button(color_frame, text="🎨 Set Color", command=self.set_color_from_rgb).pack(side=tk.LEFT, padx=2)
        tk.Button(color_frame, text="🌈 Picker", command=self.pick_color).pack(side=tk.LEFT, padx=2)

        select_frame = tk.LabelFrame(self.toolbar, text="Selection", padx=5, pady=5)
        select_frame.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        setup_shape_selection(self.canvas, root, select_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)

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
        self.current_line_points = []
        self.current_line_item = None

        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<Button-3>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<B3-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.canvas.bind("<ButtonRelease-3>", self.reset)
        root.bind("<BackSpace>", self.delete_selected_item)
        root.bind("<Delete>", self.delete_selected_item)
        root.bind("<Up>", self.keyboard_up)
        root.bind("<Down>", self.keyboard_down)
        root.bind("<Control-z>", self.undo)

        self.use_pencil()

    def use_pencil(self):
        if self.canvas.selection_mode:
            self.canvas.disable_selection_mode()
        self.eraser_mode = False
        self.fill_mode = False
        self.shape_mode = False
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.current_line_points = []
        self.current_line_item = None

    def use_eraser(self):
        if self.canvas.selection_mode:
            self.canvas.disable_selection_mode()
        self.eraser_mode = True
        self.fill_mode = False
        self.shape_mode = False

    def use_fill(self):
        if self.canvas.selection_mode:
            self.canvas.disable_selection_mode()
        self.fill_mode = True
        self.eraser_mode = False
        self.shape_mode = False

    def clear_canvas(self):
        self.canvas.delete("all")

    def pick_color(self):
        color_tuple = colorchooser.askcolor(title="Choose color")
        if color_tuple and color_tuple[0] and color_tuple[1]:
            r, g, b = map(int, color_tuple[0])
            self.r_entry.delete(0, tk.END)
            self.r_entry.insert(0, str(r))
            self.g_entry.delete(0, tk.END)
            self.g_entry.insert(0, str(g))
            self.b_entry.delete(0, tk.END)
            self.b_entry.insert(0, str(b))
            self.current_color = color_tuple[1]
            self.eraser_mode = False
            self.fill_mode = False

    def _add_color_input(self, parent, label):
        tk.Label(parent, text=label).pack(side=tk.LEFT)
        entry = tk.Entry(parent, width=4)
        entry.insert(0, "0")
        entry.pack(side=tk.LEFT)
        return entry

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

    def paint(self, event):
        x, y = event.x, event.y
        color = self.canvas["bg"] if self.eraser_mode else self.current_color
        width = self.brush_size_var.get()

        if self.last_x is not None and self.last_y is not None:
            if self.eraser_mode:
                line_id = self.canvas.create_line(
                    self.last_x, self.last_y, x, y,
                    fill=color,
                    width=width,
                    smooth=True
                )
                if hasattr(self.canvas, 'tag_new_item'):
                    self.canvas.tag_new_item(line_id)
                self.undo_stack.append(line_id)
            else:
                self.current_line_points.extend([self.last_x, self.last_y, x, y])
                if self.current_line_item:
                    self.canvas.delete(self.current_line_item)
                self.current_line_item = self.canvas.create_line(
                    *self.current_line_points,
                    fill=color,
                    width=width,
                    smooth=True
                )
        else:
            if not self.eraser_mode:
                self.current_line_points = [x, y]

        self.last_x = x
        self.last_y = y

    def reset(self, event):
        self.last_x = self.last_y = None
        if not self.eraser_mode and self.current_line_item:
            if hasattr(self.canvas, 'tag_new_item'):
                self.canvas.tag_new_item(self.current_line_item)
            self.undo_stack.append(self.current_line_item)
            self.current_line_item = None
            self.current_line_points = []

    def delete_selected_item(self, event):
        if hasattr(self.canvas, 'selected_item') and self.canvas.selected_item:
            self.canvas.delete(self.canvas.selected_item)
            self.canvas.selected_item = None

    def update_shape_button(self):
        pass

    def add_shape_sides(self):
        pass

    def remove_shape_sides(self):
        pass

    def keyboard_up(self, event):
        pass

    def keyboard_down(self, event):
        pass

    def undo(self, event):
        if self.undo_stack:
            item = self.undo_stack.pop()
            self.canvas.delete(item)

    def mouse_down(self, event):
        self.last_x = self.start_x = event.x
        self.last_y = self.start_y = event.y

    def mouse_up(self, event):
        self.last_x = self.last_y = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
