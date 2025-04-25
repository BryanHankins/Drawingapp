
def update_bbox_and_handles(app, group_tag):
    if group_tag not in app.canvas.bbox_corners:
        return

    coords = []
    for item in app.canvas.find_withtag(group_tag):
        if app.canvas.type(item) not in ("rectangle", "oval"):
            coords = app.canvas.coords(item)
            break

    if not coords:
        return

    x_coords = coords[::2]
    y_coords = coords[1::2]

    corners = [
        (min(x_coords), min(y_coords)),
        (max(x_coords), min(y_coords)),
        (max(x_coords), max(y_coords)),
        (min(x_coords), max(y_coords)),
    ]
    app.canvas.bbox_corners[group_tag] = corners

    if group_tag in app.canvas.bbox_handles:
        for handle, (cx, cy) in zip(app.canvas.bbox_handles[group_tag], corners):
            app.canvas.coords(handle, cx - 5, cy - 5, cx + 5, cy + 5)

def tag_and_select_new_shape(app, item_id):
    if hasattr(app.canvas, 'tag_new_item'):
        app.canvas.tag_new_item(item_id)
    app.canvas.selected_item = item_id

def delete_selected_item(app, event=None):
    if hasattr(app.canvas, 'selected_item') and app.canvas.selected_item:
        app.canvas.delete(app.canvas.selected_item)
        app.canvas.selected_item = None

def enable_selection_mode(app):
    if hasattr(app.canvas, 'enable_selection_mode'):
        app.canvas.enable_selection_mode()

def clear_canvas(app):
    app.canvas.delete("all")