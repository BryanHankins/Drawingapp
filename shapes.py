# File: shapes.py
import math

class Shape:
    def draw(self, canvas, x1, y1, x2, y2, color, preview):
        raise NotImplementedError("Draw method not implemented")

class Circle(Shape):
    def draw(self, canvas, x1, y1, x2, y2, color, preview):
        return canvas.create_oval(
            x1, y1, x2, y2,
            fill=color if not preview else "",
            outline=color,
            dash=(4, 2) if preview else None
        )

class Triangle(Shape):
    def __init__(self, reverse=False):
        self.reverse = reverse

    def draw(self, canvas, x1, y1, x2, y2, color, preview):
        center_x = (x1 + x2) / 2
        points = (
            [center_x, y1, x2, y2, x1, y2]
            if self.reverse else
            [center_x, y1, x1, y2, x2, y2]
        )
        return canvas.create_polygon(
            points,
            fill=color if not preview else "",
            outline=color,
            dash=(4, 2) if preview else None
        )

class Square(Shape):
    def __init__(self, reverse=False):
        self.reverse = reverse

    def draw(self, canvas, x1, y1, x2, y2, color, preview):
        coords = (x2, y2, x1, y1) if self.reverse else (x1, y1, x2, y2)
        return canvas.create_rectangle(
            *coords,
            fill=color if not preview else "",
            outline=color,
            dash=(4, 2) if preview else None
        )

class PolygonShape(Shape):
    def __init__(self, sides, reverse=False):
        self.sides = sides
        self.reverse = reverse

    def draw(self, canvas, x1, y1, x2, y2, color, preview):
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        radius = min(width, height) / 2
        angle_step = 2 * math.pi / self.sides

        points = []
        for i in range(self.sides):
            theta = -i * angle_step if self.reverse else i * angle_step
            px = center_x + radius * math.cos(theta)
            py = center_y + radius * math.sin(theta)
            points.extend([px, py])

        return canvas.create_polygon(
            points,
            fill=color if not preview else "",
            outline=color,
            dash=(4, 2) if preview else None
        )
