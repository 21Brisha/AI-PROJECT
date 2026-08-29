# ⚡ A* Maze Solver & Pathfinding Visualizer (Python & Tkinter)

An interactive, visual Maze Solver built with **Python 3** and **Tkinter** using the **A\* (A-Star) Pathfinding Algorithm**.

---

## 🚀 Features

- **Interactive Maze Canvas**:
  - ✏️ **Left-Click & Drag**: Draw walls and obstacles.
  - 🧹 **Right-Click & Drag**: Erase walls.
  - 🟢 **Start Node (Green)** & 🔴 **Goal Node (Red)** can be freely repositioned.
- **A\* Pathfinding Visualizer**:
  - Step-by-step real-time animation of explored nodes (frontier in cyan, visited in indigo, shortest path in gold).
  - Instant solve mode for instantaneous path computation and metrics.
  - Supports multiple heuristics: **Manhattan**, **Euclidean**, **Chebyshev**, and **Octile**.
  - Diagonal movement toggle (with Euclidean \(\sqrt{2}\) corner-cutting prevention).
- **Procedural Maze Generators**:
  - 🌀 **Recursive Backtracker**: Generates classic labyrinth-style mazes with winding corridors.
  - 🎲 **Random Obstacles**: Generates customizable obstacle scatter.
- **Real-time Statistics**:
  - Visited nodes count, shortest path cost/length, and calculation time in milliseconds.

---

## 🛠️ Requirements

- **Python 3.8+** (Uses Python standard library; no `pip` installations required!)

---

## 🏃 How to Run

1. Open your terminal or PowerShell in this directory:
   ```bash
   cd C:\Users\pc\.gemini\antigravity\scratch\maze_solver
   ```

2. Run the application:
   ```bash
   python main.py
   ```

---

## 🧪 Running Unit Tests

To verify the pathfinding engine and maze generation algorithms:
```bash
python -m unittest test_maze_solver.py
```

---

## 📁 Project Structure

- `main.py`: Entry point to start the Tkinter GUI.
- `gui.py`: Tkinter user interface, canvas renderer, animation loop, and controls.
- `astar.py`: Core A* pathfinding algorithm, heuristic formulas, and step-by-step generator.
- `maze_generator.py`: Procedural maze generation algorithms (Recursive Backtracker & Random).
- `test_maze_solver.py`: Automated unit tests for pathfinding and maze generators.
