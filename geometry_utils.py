import math

def rotate_selected_shape(app, angle_degrees):
    if not hasattr(app.canvas, 'selected_item') or not app.canvas.selected_item:
        return

    item = app.canvas.selected_item
    try:
        coords = app.canvas.coords(item)
        if not coords:
            return
    except:
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

        app.canvas.coords(item, *new_coords)

def crop_selected_area(app):
    if not hasattr(app.canvas, 'selected_item') or not app.canvas.selected_item:
        return

    item = app.canvas.selected_item
    try:
        coords = app.canvas.coords(item)
        if not coords or len(coords) < 4:
            return
    except:
        return

    x_coords = coords[::2]
    y_coords = coords[1::2]
    x1, y1 = min(x_coords), min(y_coords)
    x2, y2 = max(x_coords), max(y_coords)

    for other_item in app.canvas.find_all():
        if other_item != item:
            app.canvas.delete(other_item)

    app.canvas.config(scrollregion=(x1, y1, x2, y2))
    app.canvas.configure(width=int(x2 - x1), height=int(y2 - y1))
