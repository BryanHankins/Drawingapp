def undo(app, event=None):
    if app.undo_stack:
        item = app.undo_stack.pop()
        group_tag = None
        for tag in app.canvas.gettags(item):
            if tag.startswith("group_"):
                group_tag = tag
                break

        app.canvas.delete(item)

        if group_tag:
            for item in app.canvas.find_withtag(group_tag):
                app.canvas.delete(item)
            app.canvas.bbox_corners.pop(group_tag, None)
            app.canvas.bbox_handles.pop(group_tag, None)
