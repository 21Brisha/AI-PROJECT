"""
Opens the Web version of the A* Maze Solver in your default browser.
"""

import os
import webbrowser
from pathlib import Path

def open_in_browser():
    html_file = Path(__file__).parent / "web" / "index.html"
    file_uri = html_file.resolve().as_uri()
    print(f"Opening Maze Solver in browser: {file_uri}")
    webbrowser.open(file_uri)

if __name__ == "__main__":
    open_in_browser()
