import tkinter as tk
import math


def setup_shape_selection(canvas, root, toolbar):
    def activate_selection_mode():
        canvas.selection_mode = True
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<Button-3>", on_click)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<B3-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        canvas.bind("<ButtonRelease-3>", on_release)
        select_button.config(relief=tk.SUNKEN)

    def deactivate_selection_mode():
        canvas.selection_mode = False
        canvas.unbind("<Button-1>")
        canvas.unbind("<Button-3>")
        canvas.unbind("<B1-Motion>")
        canvas.unbind("<B3-Motion>")
        canvas.unbind("<ButtonRelease-1>")
        canvas.unbind("<ButtonRelease-3>")
        select_button.config(relief=tk.RAISED)

    def on_click(event):
        c = event.widget
        c.mode = "normal_move"
        c.dragging = False
        c.start_drag = (event.x, event.y)

        # Deselect previous
        for item in c.find_withtag("movable"):
            if c.type(item) == "rectangle":
                c.itemconfig(item, state='hidden')
            else:
                c.itemconfig(item, width=1, dash=())

        overlapping_items = c.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        if not overlapping_items:
            return

        movable_items = [item for item in overlapping_items if "movable" in c.gettags(item)]
        if not movable_items:
            return

        item = movable_items[-1]
        group_tag = None
        for tag in c.gettags(item):
            if tag.startswith("group_"):
                group_tag = tag
                break
        if not group_tag:
            return

        c.selected_item = group_tag

        # Show bbox
        for group_item in c.find_withtag(group_tag):
            if c.type(group_item) == "rectangle":
                c.itemconfig(group_item, state='normal')
            else:
                c.itemconfig(group_item, width=3, dash=(2, 2))

        # Check near corner?
        corners = c.bbox_corners.get(group_tag, [])
        for (cx, cy) in corners:
            if abs(event.x - cx) <= 8 and abs(event.y - cy) <= 8:
                if event.num == 3:
                    c.mode = "resize"
                elif event.num == 1:
                    c.mode = "rotate"
                break

    def on_drag(event):
        c = event.widget
        if not hasattr(c, "selected_item") or not c.selected_item:
            return
        group_tag = c.selected_item
        dx = event.x - c.start_drag[0]
        dy = event.y - c.start_drag[1]

        if c.mode == "normal_move":
            for item in c.find_withtag(group_tag):
                c.move(item, dx, dy)
            if group_tag in c.bbox_corners:
                c.bbox_corners[group_tag] = [(x+dx, y+dy) for (x, y) in c.bbox_corners[group_tag]]

        elif c.mode == "resize":
            corners = c.bbox_corners.get(group_tag)
            if corners:
                # Simple resize: scale right and bottom
                top_left = corners[0]
                bottom_right = corners[2]
                new_bottom_right = (event.x, event.y)

                # Update bbox
                for item in c.find_withtag(group_tag):
                    if c.type(item) == "rectangle":
                        c.coords(item, top_left[0], top_left[1], new_bottom_right[0], new_bottom_right[1])

        elif c.mode == "rotate":
            corners = c.bbox_corners.get(group_tag)
            if corners:
                # Find center
                (x1, y1) = corners[0]
                (x3, y3) = corners[2]
                cx = (x1 + x3) / 2
                cy = (y1 + y3) / 2

                angle = math.degrees(math.atan2(event.y - cy, event.x - cx))
                for item in c.find_withtag(group_tag):
                    if c.type(item) != "rectangle":
                        rotate_item(c, item, cx, cy, angle)

        c.start_drag = (event.x, event.y)

    def on_release(event):
        c = event.widget
        c.mode = "normal_move"

    def rotate_item(c, item, cx, cy, angle):
        coords = c.coords(item)
        new_coords = []
        radians = math.radians(angle)
        cos_val = math.cos(radians)
        sin_val = math.sin(radians)
        for i in range(0, len(coords), 2):
            x = coords[i]
            y = coords[i+1]
            dx = x - cx
            dy = y - cy
            new_x = cx + dx * cos_val - dy * sin_val
            new_y = cy + dx * sin_val + dy * cos_val
            new_coords.extend([new_x, new_y])
        c.coords(item, *new_coords)

    select_button = tk.Button(toolbar, text="🖱️ Select/Move", command=lambda: activate_selection_mode() if not canvas.selection_mode else deactivate_selection_mode())
    select_button.pack(side=tk.LEFT, padx=5)

    canvas.selection_mode = False
    canvas.enable_selection_mode = activate_selection_mode
    canvas.disable_selection_mode = deactivate_selection_mode
