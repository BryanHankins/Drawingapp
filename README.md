 Project Overview
Goal: Remake a version of the classic Microsoft Paint app — lightweight and fun, with your own modern touches.

Status: In-progress personal project.

Summary: A Python desktop app that allows users to draw shapes, freehand, and interact with a canvas in a simple GUI.

📂 Repository Structure

File/Folder	Purpose
drawing_app.py	Main application file (Tkinter-based GUI)
shape_selector.py	Logic for choosing/drawing different shapes
shapes.py	Shape classes (e.g., Circle, Square, Polygon)
requirements.txt	Lists required Python packages
drawing_app.spec	PyInstaller build specification (to package into an executable)
to do	Notes about what features you plan to add
README.md	Basic description
__pycache__/	Auto-generated Python cache files (can ignore)

⚙️ Technology Stack
Python 3.x

Tkinter — GUI toolkit

PyInstaller — for building a standalone executable (Windows app)

🛠 Strengths
✅ Clear modular design — separate files for GUI, shape selection, and shape logic.
✅ Simple and extendable — you can easily add more shapes or features later.
✅ Good starting point for a full "Paint" remake.
✅ Already prepared for packaging with PyInstaller (.spec file present).
