import tkinter as tk

def setup_shape_selection(canvas, root, toolbar):
    def activate_selection_mode():
        canvas.selection_mode = True
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

    def deactivate_selection_mode():
        canvas.selection_mode = False
        canvas.unbind("<Button-1>")
        canvas.unbind("<B1-Motion>")
        canvas.unbind("<ButtonRelease-1>")

    def on_click(event):
        canvas.itemconfig("movable", width=1, dash=())
        item = canvas.find_closest(event.x, event.y)[0]
        if canvas.type(item) in ("polygon", "oval", "rectangle", "line"):
            canvas.itemconfig(item, width=3, dash=(2, 2))
            canvas.selected_item = item
            canvas.last_drag = (event.x, event.y)

    def on_drag(event):
        if hasattr(canvas, 'selected_item'):
            dx = event.x - canvas.last_drag[0]
            dy = event.y - canvas.last_drag[1]
            canvas.move(canvas.selected_item, dx, dy)
            canvas.last_drag = (event.x, event.y)

    def on_release(event):
        canvas.last_drag = None

    def tag_new_item(item_id):
        canvas.addtag_withtag("movable", item_id)

    canvas.tag_new_item = tag_new_item
    canvas.selection_mode = False
    canvas.enable_selection_mode = activate_selection_mode
    canvas.disable_selection_mode = deactivate_selection_mode

    select_button = tk.Button(toolbar, text="🖱️ Select/Move", command=activate_selection_mode)
    select_button.pack(side=tk.LEFT, padx=5)
