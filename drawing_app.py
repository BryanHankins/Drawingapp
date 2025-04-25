# File: drawing_app.py

import tkinter as tk
from tkinter import colorchooser, messagebox
from shape_selector import setup_shape_selection
from shapes import Circle, Triangle, Square, PolygonShape
from undo_utils import undo
from geometry_utils import rotate_selected_shape, crop_selected_area
from color_utils import set_color_from_rgb, pick_color, add_color_input
from selection_helpers import update_bbox_and_handles
from shape_management import finalize_shape_creation, draw_shape_preview
from modes import set_mode_pencil, set_mode_eraser, set_mode_fill, use_shape_mode, use_pencil, use_eraser, use_fill



class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mare Drawing App")
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_canvas)
        file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        self.toolbar = tk.Frame(root, pady=2, relief=tk.RAISED, bd=1)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self._build_clipboard_section()
        self._build_image_section()
        self._build_tools_section()
        self._build_shapes_section()
        self._build_style_section()
        self._build_size_section()
        self._build_color_section()

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        setup_shape_selection(self.canvas, root, self.toolbar)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.enable_selection_mode()

        self.shapes = ["Circle", "Triangle", "Square"]
        self.shape_index = 0
        self.custom_mode = False
        self.current_shape_sides = 0
        self.reverse_direction = False
        self.preview_shape = None
        self.selected_item = None
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
        root.bind("<Control-z>", lambda e: undo(self))

        # set_mode_pencil(self)
        use_pencil(self)
        

    def _build_clipboard_section(self):
        f = tk.LabelFrame(self.toolbar, text="Clipboard")
        f.pack(side=tk.LEFT, padx=5)
        tk.Button(f, text="Paste").pack(side=tk.TOP, pady=2)
        tk.Button(f, text="Cut").pack(side=tk.TOP, pady=2)
        tk.Button(f, text="Copy").pack(side=tk.TOP, pady=2)

    def _build_image_section(self):
        f = tk.LabelFrame(self.toolbar, text="Image")
        f.pack(side=tk.LEFT, padx=5)
        tk.Button(f, text="Select", command=self.enable_selection_mode).pack(side=tk.TOP, pady=2)
        tk.Button(f, text="Crop", command=lambda: crop_selected_area(self)).pack(side=tk.TOP, pady=2)
        tk.Button(f, text="Rotate Left", command=lambda: rotate_selected_shape(self, -15)).pack(side=tk.TOP, pady=2)
        tk.Button(f, text="Rotate Right", command=lambda: rotate_selected_shape(self, 15)).pack(side=tk.TOP, pady=2)

    def _build_tools_section(self):
        f = tk.LabelFrame(self.toolbar, text="Tools")
        f.pack(side=tk.LEFT, padx=5)
        tk.Button(f, text="✏️ Pencil", command=lambda: use_pencil(self)).pack(side=tk.LEFT, padx=2)
        tk.Button(f, text="🧽 Eraser", command=lambda: use_eraser(self)).pack(side=tk.LEFT, padx=2)
        tk.Button(f, text="🪣 Fill", command=lambda: use_fill(self)).pack(side=tk.LEFT, padx=2)

    def _build_shapes_section(self):
        f = tk.LabelFrame(self.toolbar, text="Shapes")
        f.pack(side=tk.LEFT, padx=5)
        self.shape_button = tk.Button(f, text="🔄 Shape: Circle", command=self.update_shape_button)
        self.shape_button.pack(side=tk.TOP, padx=2)
        tk.Button(f, text="🔼 Up", command=self.add_shape_sides).pack(side=tk.LEFT, padx=2)
        tk.Button(f, text="🔽 Down", command=self.remove_shape_sides).pack(side=tk.LEFT, padx=2)

    def _build_style_section(self):
        f = tk.LabelFrame(self.toolbar, text="Style")
        f.pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(f, tk.StringVar(value="Solid"), "Solid", "Dashed").pack()
        tk.OptionMenu(f, tk.StringVar(value="Fill"), "Fill", "No Fill").pack()

    def _build_size_section(self):
        f = tk.LabelFrame(self.toolbar, text="Size")
        f.pack(side=tk.LEFT, padx=5)
        self.brush_size_var = tk.IntVar(value=2)
        tk.OptionMenu(f, self.brush_size_var, 1, 2, 4, 8, 10).pack()
    print("use_pencil(self)")
    def _build_color_section(self):
        f = tk.LabelFrame(self.toolbar, text="Colors")
        f.pack(side=tk.LEFT, padx=5)
        self.r_entry = add_color_input(f, "R:")
        self.g_entry = add_color_input(f, "G:")
        self.b_entry = add_color_input(f, "B:")
        tk.Button(f, text="🎨 Set Color", command=lambda: set_color_from_rgb(self)).pack(side=tk.LEFT, padx=2)
        tk.Button(f, text="🌈 Picker", command=lambda: pick_color(self)).pack(side=tk.LEFT, padx=2)

    def clear_canvas(self):
        self.canvas.delete("all")

    def enable_selection_mode(self):
        if hasattr(self.canvas, 'enable_selection_mode'):
            self.canvas.enable_selection_mode()

    def delete_selected_item(self, event=None):
        if hasattr(self.canvas, 'selected_item') and self.canvas.selected_item:
            self.canvas.delete(self.canvas.selected_item)
            self.canvas.selected_item = None

    def keyboard_up(self, event):
        self.reverse_direction = True
        if self.is_dragging:
            draw_shape_preview(self, self.start_x, self.start_y, self.last_x, self.last_y)

    def keyboard_down(self, event):
        self.reverse_direction = False
        if self.is_dragging:
            draw_shape_preview(self, self.start_x, self.start_y, self.last_x, self.last_y)

    def paint(self, event):
        x, y = event.x, event.y
        if self.shape_mode:
            if self.start_x is None or self.start_y is None:
                self.start_x, self.start_y = x, y
            self.is_dragging = True
            self.last_x, self.last_y = x, y
            draw_shape_preview(self, self.start_x, self.start_y, x, y)

    def reset(self, event):
        if self.shape_mode and self.is_dragging:
            self.is_dragging = False
            finalize_shape_creation(self, self.start_x, self.start_y, event.x, event.y)
            group_tag = f"group_{self.selected_item}"
            update_bbox_and_handles(self, group_tag)
            return

        self.last_x = self.last_y = None
        if not self.eraser_mode and self.current_line_item:
            if hasattr(self.canvas, 'tag_new_item'):
                self.canvas.tag_new_item(self.current_line_item)
            self.undo_stack.append(self.current_line_item)
            self.current_line_item = None
            self.current_line_points = []

    def update_shape_button(self):
        self.shape_index += 1
        if self.shape_index >= len(self.shapes):
            self.shape_index = 0
            self.custom_mode = True
            self.current_shape_sides = 5
        else:
            self.custom_mode = False

        self.shape_mode = True
        if self.custom_mode:
            text = f"Polygon ({self.current_shape_sides} sides)"
        else:
            text = self.shapes[self.shape_index]
        self.shape_button.config(text=f"🔄 Shape: {text}")

    def add_shape_sides(self):
        if not self.custom_mode:
            return
        self.current_shape_sides += 1
        if self.current_shape_sides < 3:
            self.current_shape_sides = 3
        self.shape_button.config(text=f"🔄 Shape: Polygon ({self.current_shape_sides} sides)")

    def remove_shape_sides(self):
        if not self.custom_mode:
            return
        self.current_shape_sides -= 1
        if self.current_shape_sides < 3:
            self.current_shape_sides = 3
        self.shape_button.config(text=f"🔄 Shape: Polygon ({self.current_shape_sides} sides)")

    def mouse_down(self, event):
        self.last_x = self.start_x = event.x
        self.last_y = self.start_y = event.y

    def mouse_up(self, event):
        self.last_x = self.last_y = None


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
