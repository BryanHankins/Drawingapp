def set_mode_pencil(app):
    if app.canvas.selection_mode:
        app.canvas.disable_selection_mode()
    app.canvas.bind("<B1-Motion>", app.paint)
    app.canvas.bind("<ButtonRelease-1>", app.reset)
    app.eraser_mode = False
    app.fill_mode = False
    app.shape_mode = False
    app.current_line_points = []
    app.current_line_item = None

def set_mode_eraser(app):
    app.eraser_mode = True
    app.fill_mode = False
    app.shape_mode = False

def set_mode_fill(app):
    app.canvas.bind("<Button-1>", app.fill_color)
    app.fill_mode = True
    app.eraser_mode = False
    app.shape_mode = False


def use_pencil(app):
    if app.canvas.selection_mode:
        app.canvas.disable_selection_mode()
    app.eraser_mode = False
    app.fill_mode = False
    app.shape_mode = False
    app.canvas.bind("<B1-Motion>", app.paint)
    app.canvas.bind("<ButtonRelease-1>", app.reset)
    app.current_line_points = []
    app.current_line_item = None

def use_eraser(app):
    if app.canvas.selection_mode:
        app.canvas.disable_selection_mode()
    set_mode_eraser(app)

def use_fill(app):
    if app.canvas.selection_mode:
        app.canvas.disable_selection_mode()
    set_mode_fill(app)

def use_shape_mode(app):
    if app.canvas.selection_mode:
        app.canvas.disable_selection_mode()
    app.eraser_mode = False
    app.fill_mode = False
    app.shape_mode = True

