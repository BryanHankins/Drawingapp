
import unittest
import tkinter as tk
from drawing_app import DrawingApp

# Import utils directly
from color_utils import rgb_to_hex, set_color_from_rgb
from undo_utils import undo_last_action
from geometry_utils import rotate_selected_shape, crop_selected_area

class DummyCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_item = None
        self.selected_bbox = None
        self.bbox_corners = {}
        self.bbox_handles = {}

class TestColorUtils(unittest.TestCase):
    def test_rgb_to_hex_valid(self):
        self.assertEqual(rgb_to_hex(255, 0, 0), '#ff0000')
        self.assertEqual(rgb_to_hex(0, 255, 0), '#00ff00')
        self.assertEqual(rgb_to_hex(0, 0, 255), '#0000ff')

    def test_rgb_to_hex_invalid(self):
        with self.assertRaises(ValueError):
            rgb_to_hex(-1, 256, 300)

class TestUndoUtils(unittest.TestCase):
    def test_undo_empty_stack(self):
        canvas = DummyCanvas()
        app = type("App", (object,), {"canvas": canvas, "undo_stack": []})
        undo_last_action(app)  # Should not raise error

class TestGeometryUtils(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = DrawingApp(self.root)
        self.app.canvas.selected_item = self.app.canvas.create_polygon(100, 100, 150, 100, 125, 150, fill="blue")

    def tearDown(self):
        self.root.destroy()

    def test_rotate_selected_shape(self):
        rotate_selected_shape(self.app, 90)
        coords = self.app.canvas.coords(self.app.canvas.selected_item)
        self.assertEqual(len(coords), 6)  # Triangle

    def test_crop_selected_area(self):
        crop_selected_area(self.app)
        self.assertTrue(self.app.canvas.winfo_width() > 0)

if __name__ == '__main__':
    unittest.main()
