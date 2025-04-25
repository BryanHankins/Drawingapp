# File: shape_management.py

from shapes import Circle, Triangle, Square, PolygonShape
from selection_helpers import update_bbox_and_handles

def get_shape(app):
    if app.custom_mode:
        return PolygonShape(app.current_shape_sides, app.reverse_direction)
    shape_type = app.shapes[app.shape_index]
    if shape_type == "Circle":
        return Circle()
    elif shape_type == "Triangle":
        return Triangle(app.reverse_direction)
    elif shape_type == "Square":
        return Square(app.reverse_direction)

def draw_shape_preview(app, x1, y1, x2, y2):
    if app.preview_shape:
        app.canvas.delete(app.preview_shape)
    shape = get_shape(app)
    app.preview_shape = shape.draw(app.canvas, x1, y1, x2, y2, color=app.current_color, preview=True)

def finalize_shape_creation(app, x1, y1, x2, y2):
    if app.preview_shape:
        app.canvas.delete(app.preview_shape)
        app.preview_shape = None

    shape = get_shape(app)
    final_shape = shape.draw(app.canvas, x1, y1, x2, y2, color=app.current_color, preview=False)

    coords = app.canvas.coords(final_shape)
    x_coords = coords[::2]
    y_coords = coords[1::2]

    bbox = app.canvas.create_rectangle(
        min(x_coords), min(y_coords),
        max(x_coords), max(y_coords),
        outline="blue", dash=(3, 3)
    )

    group_tag = f"group_{final_shape}"
    app.canvas.addtag_withtag(group_tag, final_shape)
    app.canvas.addtag_withtag(group_tag, bbox)
    app.canvas.addtag_withtag("movable", group_tag)

    app.canvas.itemconfig(bbox, state='hidden')

    corners = [
        (min(x_coords), min(y_coords)),
        (max(x_coords), min(y_coords)),
        (max(x_coords), max(y_coords)),
        (min(x_coords), max(y_coords)),
    ]
    if not hasattr(app.canvas, 'bbox_corners'):
        app.canvas.bbox_corners = {}
    app.canvas.bbox_corners[group_tag] = corners

    handle_radius = 5
    handles = []
    for (cx, cy) in corners:
        handle = app.canvas.create_oval(
            cx - handle_radius, cy - handle_radius,
            cx + handle_radius, cy + handle_radius,
            fill="blue", outline="black"
        )
        app.canvas.addtag_withtag(f"handle_{group_tag}", handle)
        handles.append(handle)

    if not hasattr(app.canvas, 'bbox_handles'):
        app.canvas.bbox_handles = {}
    app.canvas.bbox_handles[group_tag] = handles

    app.undo_stack.append(final_shape)
    app.undo_stack.append(bbox)
    for handle in handles:
        app.undo_stack.append(handle)

    update_bbox_and_handles(app, group_tag)
