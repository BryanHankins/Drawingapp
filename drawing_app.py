# File: drawing_app.py

import tkinter as tk
from tkinter import colorchooser,  messagebox
import math
from shape_selector import setup_shape_selection
from shapes import Circle, Triangle, Square, PolygonShape

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


        # ==== Clipboard ====
        clipboard_frame = tk.LabelFrame(self.toolbar, text="Clipboard")
        clipboard_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(clipboard_frame, text="Paste").pack(side=tk.TOP, pady=2)
        tk.Button(clipboard_frame, text="Cut").pack(side=tk.TOP, pady=2)
        tk.Button(clipboard_frame, text="Copy").pack(side=tk.TOP, pady=2)

        # ==== Image ====
        image_frame = tk.LabelFrame(self.toolbar, text="Image")
        image_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(image_frame, text="Select", command=self.enable_selection_mode).pack(side=tk.TOP, pady=2)
        tk.Button(image_frame, text="Crop", command=self.crop_selected_area).pack(side=tk.TOP, pady=2)
        tk.Button(image_frame, text="Rotate Left", command=self.rotate_left).pack(side=tk.TOP, pady=2)
        tk.Button(image_frame, text="Rotate Right", command=self.rotate_right).pack(side=tk.TOP, pady=2)

        # ==== Tools ====
        tools_frame = tk.LabelFrame(self.toolbar, text="Tools")
        tools_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(tools_frame, text="✏️ Pencil", command=self.use_pencil).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="🧽 Eraser", command=self.use_eraser).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="🪣 Fill", command=self.use_fill).pack(side=tk.LEFT, padx=2)

        # ==== Shapes ====
        shapes_frame = tk.LabelFrame(self.toolbar, text="Shapes")
        shapes_frame.pack(side=tk.LEFT, padx=5)
        self.shape_button = tk.Button(shapes_frame, text="🔄 Shape: Circle", command=self.update_shape_button)
        self.shape_button.pack(side=tk.TOP, padx=2)
        self.up_button = tk.Button(shapes_frame, text="🔼 Up", command=self.add_shape_sides)
        self.up_button.pack(side=tk.LEFT, padx=2)
        self.down_button = tk.Button(shapes_frame, text="🔽 Down", command=self.remove_shape_sides)
        self.down_button.pack(side=tk.LEFT, padx=2)

        # ==== Style ====
        stroke_fill_frame = tk.LabelFrame(self.toolbar, text="Style")
        stroke_fill_frame.pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(stroke_fill_frame, tk.StringVar(value="Solid"), "Solid", "Dashed").pack()
        tk.OptionMenu(stroke_fill_frame, tk.StringVar(value="Fill"), "Fill", "No Fill").pack()

        # ==== Size ====
        size_frame = tk.LabelFrame(self.toolbar, text="Size")
        size_frame.pack(side=tk.LEFT, padx=5)
        self.brush_size_var = tk.IntVar(value=2)
        tk.OptionMenu(size_frame, self.brush_size_var, 1, 2, 4, 8, 10).pack()

        # ==== Colors ====
        color_frame = tk.LabelFrame(self.toolbar, text="Colors")
        color_frame.pack(side=tk.LEFT, padx=5)

        self.r_entry = self._add_color_input(color_frame, "R:")
        self.g_entry = self._add_color_input(color_frame, "G:")
        self.b_entry = self._add_color_input(color_frame, "B:")

        tk.Button(color_frame, text="🎨 Set Color", command=self.set_color_from_rgb).pack(side=tk.LEFT, padx=2)
        tk.Button(color_frame, text="🌈 Picker", command=self.pick_color).pack(side=tk.LEFT, padx=2)

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        setup_shape_selection(self.canvas, root, self.toolbar)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.enable_selection_mode()  # 🔥 Start in Select/Move mode by default

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

    # ========== HELPER METHODS ==========

    def use_shape_mode(self):
        if self.canvas.selection_mode:
            self.canvas.disable_selection_mode()
        self.eraser_mode = False
        self.fill_mode = False
        self.shape_mode = True

    def enable_selection_mode(self):
        if hasattr(self.canvas, 'enable_selection_mode'):
            self.canvas.enable_selection_mode()

    def undo(self, event=None):
        if self.undo_stack:
            item = self.undo_stack.pop()
            self.canvas.delete(item)

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



    def clear_canvas(self):
        self.canvas.delete("all")
    def tag_and_select_new_shape(self, item_id):
        if hasattr(self.canvas, 'tag_new_item'):
            self.canvas.tag_new_item(item_id)
        self.canvas.selected_item = item_id

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

        if self.shape_mode:
            if self.start_x is None or self.start_y is None:
                self.start_x = x
                self.start_y = y

            self.is_dragging = True
            self.last_x = x
            self.last_y = y
            self.draw_shape_preview(self.start_x, self.start_y, x, y)
            return

    def reset(self, event):
        if self.shape_mode and self.is_dragging:
            self.is_dragging = False
            if self.preview_shape:
                self.canvas.delete(self.preview_shape)

            if self.custom_mode:
                shape = PolygonShape(self.current_shape_sides, self.reverse_direction)
            else:
                shape_type = self.shapes[self.shape_index]
                if shape_type == "Circle":
                    shape = Circle()
                elif shape_type == "Triangle":
                    shape = Triangle(self.reverse_direction)
                elif shape_type == "Square":
                    shape = Square(self.reverse_direction)

            final_shape = shape.draw(
                self.canvas,
                self.start_x, self.start_y,
                event.x, event.y,
                color=self.current_color,
                preview=False
            )

            coords = self.canvas.coords(final_shape)
            x_coords = coords[::2]
            y_coords = coords[1::2]

            bbox = self.canvas.create_rectangle(
                min(x_coords), min(y_coords),
                max(x_coords), max(y_coords),
                outline="blue", dash=(3, 3)
            )

            group_tag = f"group_{final_shape}"
            self.canvas.addtag_withtag(group_tag, final_shape)
            self.canvas.addtag_withtag(group_tag, bbox)
            self.canvas.addtag_withtag("movable", group_tag)

            self.canvas.itemconfig(bbox, state='hidden')

            if not hasattr(self.canvas, 'bbox_corners'):
                self.canvas.bbox_corners = {}
            self.canvas.bbox_corners[group_tag] = [
                (min(x_coords), min(y_coords)),
                (max(x_coords), min(y_coords)),
                (max(x_coords), max(y_coords)),
                (min(x_coords), max(y_coords)),
            ]

            self.undo_stack.append(final_shape)
            self.undo_stack.append(bbox)

            return

        self.last_x = self.last_y = None
        if not self.eraser_mode and self.current_line_item:
            if hasattr(self.canvas, 'tag_new_item'):
                self.canvas.tag_new_item(self.current_line_item)
            self.undo_stack.append(self.current_line_item)
            self.current_line_item = None
            self.current_line_points = []



    def use_fill(self):
        if self.canvas.selection_mode:
            self.canvas.disable_selection_mode()
        self.fill_mode = True
        self.eraser_mode = False
        self.shape_mode = False
        self.canvas.bind("<Button-1>", self.fill_color)

    def fill_color(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if item:
            self.canvas.itemconfig(item, fill=self.current_color)

    def copy_item(self):
        if hasattr(self.canvas, 'selected_item') and self.canvas.selected_item:
            self.clipboard_item = self.canvas.selected_item

    def cut_item(self):
        if hasattr(self.canvas, 'selected_item') and self.canvas.selected_item:
            self.clipboard_item = self.canvas.selected_item
            self.canvas.delete(self.canvas.selected_item)
            self.canvas.selected_item = None

    def paste_item(self):
        if self.clipboard_item:
            coords = self.canvas.coords(self.clipboard_item)
            if coords:
                new_coords = [c + 10 for c in coords]
                new_item = self.canvas.create_polygon(new_coords, fill=self.current_color)
                self.canvas.addtag_withtag("movable", new_item)
                self.undo_stack.append(new_item)

    def rotate_selected_shape(self, angle_degrees):
        if not hasattr(self.canvas, 'selected_item') or not self.canvas.selected_item:
            messagebox.showwarning("Warning", "No object selected to rotate!")
            return

        item = self.canvas.selected_item
        try:
            coords = self.canvas.coords(item)
            if not coords:
                return
        except tk.TclError:
            return

        if len(coords) >= 4:
            x_coords = coords[::2]
            y_coords = coords[1::2]
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)

            radians = math.radians(angle_degrees)
            cos_val = math.cos(radians)
            sin_val = math.sin(radians)

            new_coords = []
            for x, y in zip(x_coords, y_coords):
                dx = x - center_x
                dy = y - center_y
                new_x = center_x + dx * cos_val - dy * sin_val
                new_y = center_y + dx * sin_val + dy * cos_val
                new_coords.extend([new_x, new_y])

            self.canvas.coords(item, *new_coords)

    def double_click_activate_selection(self, event):
        self.enable_selection_mode()
        if hasattr(self.canvas, 'selected_item') and self.canvas.selected_item:
            self.canvas.itemconfig(self.canvas.selected_item, width=1, dash=())
            if hasattr(self.canvas, 'selected_bbox') and self.canvas.selected_bbox:
                self.canvas.delete(self.canvas.selected_bbox)
                self.canvas.selected_bbox = None

        closest_items = self.canvas.find_closest(event.x, event.y)
        if closest_items:
            item = closest_items[0]
            try:
                item_type = self.canvas.type(item)
                if item_type in ("polygon", "oval", "rectangle", "line"):
                    self.canvas.itemconfig(item, width=3, dash=(2, 2))
                    self.canvas.selected_item = item

                    coords = self.canvas.coords(item)
                    x_coords = coords[::2]
                    y_coords = coords[1::2]
                    bbox = self.canvas.create_rectangle(min(x_coords), min(y_coords), max(x_coords), max(y_coords), outline="blue", dash=(3, 3))
                    self.canvas.selected_bbox = bbox
            except tk.TclError:
                pass


    def delete_selected_item(self, event):
        if hasattr(self.canvas, 'selected_item') and self.canvas.selected_item:
            self.canvas.delete(self.canvas.selected_item)
            self.canvas.selected_item = None

    def update_shape_button(self):
        self.shape_index += 1
        if self.shape_index >= len(self.shapes):
            self.shape_index = 0
            self.custom_mode = True
            self.current_shape_sides = 5
        else:
            self.custom_mode = False

        self.use_shape_mode()

        if self.custom_mode:
            shape_text = f"Polygon ({self.current_shape_sides} sides)"
        else:
            shape_text = self.shapes[self.shape_index]

        self.shape_button.config(text=f"🔄 Shape: {shape_text}")

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

    def rotate_left(self):
        self.rotate_selected_shape(-15)

    def rotate_right(self):
        self.rotate_selected_shape(15)


    def crop_selected_area(self):
        if not hasattr(self.canvas, 'selected_item') or not self.canvas.selected_item:
            return

        item = self.canvas.selected_item
        try:
            coords = self.canvas.coords(item)
            if not coords or len(coords) < 4:
                return
        except tk.TclError:
            return

        x_coords = coords[::2]
        y_coords = coords[1::2]
        x1, y1 = min(x_coords), min(y_coords)
        x2, y2 = max(x_coords), max(y_coords)

        # Clear everything else
        all_items = self.canvas.find_all()
        for other_item in all_items:
            if other_item != item:
                self.canvas.delete(other_item)

        # Resize canvas to crop area
        self.canvas.config(scrollregion=(x1, y1, x2, y2))
        self.canvas.configure(width=int(x2 - x1), height=int(y2 - y1))

    def keyboard_up(self, event):
        self.reverse_direction = True
        if self.is_dragging:
            self.draw_shape_preview(self.start_x, self.start_y, self.last_x, self.last_y)

    def keyboard_down(self, event):
        self.reverse_direction = False
        if self.is_dragging:
            self.draw_shape_preview(self.start_x, self.start_y, self.last_x, self.last_y)

    def draw_shape_preview(self, x1, y1, x2, y2):
        if self.preview_shape:
            self.canvas.delete(self.preview_shape)

        if self.custom_mode:
            shape = PolygonShape(self.current_shape_sides, self.reverse_direction)
        else:
            shape_type = self.shapes[self.shape_index]
            if shape_type == "Circle":
                shape = Circle()
            elif shape_type == "Triangle":
                shape = Triangle(self.reverse_direction)
            elif shape_type == "Square":
                shape = Square(self.reverse_direction)

        self.preview_shape = shape.draw(self.canvas, x1, y1, x2, y2, color=self.current_color, preview=True)

    def mouse_down(self, event):
        self.last_x = self.start_x = event.x
        self.last_y = self.start_y = event.y

    def mouse_up(self, event):
        self.last_x = self.last_y = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
