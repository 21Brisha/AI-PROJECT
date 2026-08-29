"""
Interactive GUI for A* Maze Solver using Tkinter.
Features smooth visual animation, custom maze drawing, procedural maze generators,
heuristics selection, diagonal movement toggle, and detailed search metrics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
from typing import Tuple, Optional, Set, List, Dict
from astar import astar_generator, astar_solve, HEURISTICS
from maze_generator import (
    generate_blank_grid,
    generate_random_walls,
    generate_recursive_backtracker_maze
)

Coord = Tuple[int, int]

# Color Palette (Modern Dark Theme)
COLOR_BG = "#1e1e2e"
COLOR_SIDEBAR = "#181825"
COLOR_CARD = "#252538"
COLOR_BORDER = "#313244"
COLOR_TEXT = "#cdd6f4"
COLOR_TEXT_DIM = "#a6adc8"
COLOR_ACCENT = "#89b4fa"

# Grid Cell Colors
COLOR_EMPTY = "#1e1e2e"
COLOR_GRID_LINE = "#2a2b3d"
COLOR_WALL = "#45475a"
COLOR_START = "#2ed573"       # Vivid Green
COLOR_GOAL = "#ff4757"        # Vivid Red
COLOR_OPEN = "#00d2d3"        # Cyan Frontier
COLOR_CLOSED = "#5f27cd"      # Deep Purple / Indigo
COLOR_CURRENT = "#ff9ff3"     # Pink Current Focus
COLOR_PATH = "#ffa502"        # Bright Gold / Orange

class MazeSolverGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("A* Maze Solver & Pathfinding Visualizer")
        self.root.configure(bg=COLOR_BG)
        self.root.geometry("1120x760")
        self.root.minsize(980, 680)

        # Default Grid Configuration (Odd numbers work best with Recursive Backtracker)
        self.rows = 27
        self.cols = 37
        self.cell_size = 20

        # State
        self.start_pos: Coord = (1, 1)
        self.goal_pos: Coord = (self.rows - 2, self.cols - 2)
        self.grid: List[List[int]] = generate_blank_grid(self.rows, self.cols)
        
        # UI & Animation control
        self.is_running = False
        self.is_paused = False
        self.generator = None
        self.current_tool = "wall"  # "wall", "erase", "start", "goal"
        self.mouse_pressed = False
        self.visited_cells: Set[Coord] = set()
        self.path_cells: List[Coord] = []
        self.cell_rect_ids: Dict[Coord, int] = {}
        self.start_marker_id = None
        self.goal_marker_id = None

        self._setup_styles()
        self._build_layout()
        self._init_grid_canvas()
        self._update_all_cells()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Sidebar.TFrame", background=COLOR_SIDEBAR)
        style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")
        
        style.configure("TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=COLOR_SIDEBAR, foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        style.configure("Section.TLabel", background=COLOR_CARD, foreground=COLOR_ACCENT, font=("Segoe UI", 10, "bold"))
        style.configure("Value.TLabel", background=COLOR_CARD, foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.configure("Status.TLabel", background=COLOR_CARD, foreground="#a6e3a1", font=("Segoe UI", 10, "bold"))
        
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background="#2ed573", foreground="#1e1e2e")
        style.map("Primary.TButton", background=[("active", "#26af5f"), ("disabled", "#3a4a40")])
        
        style.configure("Action.TButton", font=("Segoe UI", 9), background="#313244", foreground=COLOR_TEXT)
        style.map("Action.TButton", background=[("active", "#45475a")])

        style.configure("Danger.TButton", font=("Segoe UI", 9), background="#ff4757", foreground="#ffffff")
        style.map("Danger.TButton", background=[("active", "#d63031")])

        style.configure("TCombobox", fieldbackground="#313244", background="#45475a", foreground="#ffffff")
        style.configure("TCheckbutton", background=COLOR_CARD, foreground=COLOR_TEXT, font=("Segoe UI", 9))
        style.map("TCheckbutton", background=[("active", COLOR_CARD)])

    def _build_layout(self):
        # Main layout: Left sidebar for controls, Right panel for grid canvas
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=300, padding=12)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        self.canvas_container = tk.Frame(self.root, bg=COLOR_BG, padx=12, pady=12)
        self.canvas_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar_contents()

    def _build_sidebar_contents(self):
        # App Title
        title_label = ttk.Label(self.sidebar, text="⚡ A* Maze Solver", style="Header.TLabel")
        title_label.pack(anchor="w", pady=(4, 12))

        # --- 1. Actions Card ---
        actions_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        actions_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(actions_card, text="Execution Controls", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        btn_row1 = tk.Frame(actions_card, bg=COLOR_CARD)
        btn_row1.pack(fill=tk.X, pady=2)
        self.btn_solve = tk.Button(
            btn_row1, text="▶ Visual Solve", bg="#2ed573", fg="#1e1e2e", 
            font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#26af5f",
            command=self.start_visualization, cursor="hand2"
        )
        self.btn_solve.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_instant = tk.Button(
            btn_row1, text="⚡ Instant", bg="#70a1ff", fg="#1e1e2e", 
            font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#1e90ff",
            command=self.solve_instant, cursor="hand2"
        )
        self.btn_instant.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        btn_row2 = tk.Frame(actions_card, bg=COLOR_CARD)
        btn_row2.pack(fill=tk.X, pady=4)
        
        self.btn_step = tk.Button(
            btn_row2, text="⏭ Step", bg="#313244", fg=COLOR_TEXT,
            font=("Segoe UI", 9), relief="flat", activebackground="#45475a",
            command=self.step_visualization, cursor="hand2"
        )
        self.btn_step.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_stop = tk.Button(
            btn_row2, text="⏹ Stop", bg="#ff4757", fg="#ffffff",
            font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#d63031",
            command=self.stop_visualization, cursor="hand2"
        )
        self.btn_stop.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        btn_row3 = tk.Frame(actions_card, bg=COLOR_CARD)
        btn_row3.pack(fill=tk.X, pady=2)
        
        self.btn_clear_path = tk.Button(
            btn_row3, text="🔄 Clear Path", bg="#313244", fg=COLOR_TEXT,
            font=("Segoe UI", 8), relief="flat", activebackground="#45475a",
            command=self.clear_path_visuals, cursor="hand2"
        )
        self.btn_clear_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_clear_all = tk.Button(
            btn_row3, text="🗑 Clear Grid", bg="#313244", fg=COLOR_TEXT,
            font=("Segoe UI", 8), relief="flat", activebackground="#45475a",
            command=self.clear_all, cursor="hand2"
        )
        self.btn_clear_all.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        # --- 2. Maze Generator Card ---
        gen_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        gen_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(gen_card, text="Generate Mazes", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        btn_gen_backtracker = tk.Button(
            gen_card, text="🌀 Recursive Maze", bg="#313244", fg=COLOR_TEXT,
            font=("Segoe UI", 9), relief="flat", activebackground="#45475a",
            command=self.generate_backtracker_maze, cursor="hand2"
        )
        btn_gen_backtracker.pack(fill=tk.X, pady=2)

        btn_gen_random = tk.Button(
            gen_card, text="🎲 Random Obstacles (30%)", bg="#313244", fg=COLOR_TEXT,
            font=("Segoe UI", 9), relief="flat", activebackground="#45475a",
            command=self.generate_random_obstacles, cursor="hand2"
        )
        btn_gen_random.pack(fill=tk.X, pady=2)

        # --- 3. Algorithm Settings Card ---
        settings_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        settings_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(settings_card, text="Algorithm Options", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        # Heuristic Dropdown
        ttk.Label(settings_card, text="Heuristic:").pack(anchor="w")
        self.heuristic_var = tk.StringVar(value="Manhattan")
        self.combo_heuristic = ttk.Combobox(
            settings_card, textvariable=self.heuristic_var,
            values=list(HEURISTICS.keys()), state="readonly"
        )
        self.combo_heuristic.pack(fill=tk.X, pady=(2, 6))

        # Diagonal Movement Checkbox
        self.diagonal_var = tk.BooleanVar(value=False)
        self.chk_diagonal = ttk.Checkbutton(
            settings_card, text="Allow Diagonal Moves", variable=self.diagonal_var
        )
        self.chk_diagonal.pack(anchor="w", pady=(0, 6))

        # Animation Speed Slider
        ttk.Label(settings_card, text="Animation Delay (ms):").pack(anchor="w")
        self.speed_var = tk.IntVar(value=15)
        self.slider_speed = tk.Scale(
            settings_card, from_=1, to=100, orient=tk.HORIZONTAL,
            variable=self.speed_var, bg=COLOR_CARD, fg=COLOR_TEXT,
            troughcolor="#313244", highlightthickness=0
        )
        self.slider_speed.pack(fill=tk.X, pady=(0, 2))

        # --- 4. Tool Selection Mode ---
        tool_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        tool_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tool_card, text="Mouse Edit Mode", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        self.tool_var = tk.StringVar(value="wall")
        tool_choices = [
            ("✏️ Wall (Left Click)", "wall"),
            ("🧹 Erase (Right Click)", "erase"),
            ("🟢 Move Start", "start"),
            ("🔴 Move Goal", "goal")
        ]
        for text, mode in tool_choices:
            rb = tk.Radiobutton(
                tool_card, text=text, value=mode, variable=self.tool_var,
                bg=COLOR_CARD, fg=COLOR_TEXT, selectcolor="#313244",
                activebackground=COLOR_CARD, activeforeground="#ffffff",
                font=("Segoe UI", 8), anchor="w"
            )
            rb.pack(fill=tk.X)

        # --- 5. Metrics & Status Card ---
        metrics_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=10)
        metrics_card.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Label(metrics_card, text="Statistics", style="Section.TLabel").pack(anchor="w", pady=(0, 4))

        self.lbl_status = ttk.Label(metrics_card, text="Status: Ready", style="Status.TLabel")
        self.lbl_status.pack(anchor="w", pady=1)

        self.lbl_visited = ttk.Label(metrics_card, text="Visited Nodes: 0", style="TLabel")
        self.lbl_visited.pack(anchor="w", pady=1)

        self.lbl_length = ttk.Label(metrics_card, text="Path Cost: -", style="TLabel")
        self.lbl_length.pack(anchor="w", pady=1)

        self.lbl_time = ttk.Label(metrics_card, text="Time: 0 ms", style="TLabel")
        self.lbl_time.pack(anchor="w", pady=1)

    def _init_grid_canvas(self):
        # Calculate canvas pixel dimensions
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size

        self.canvas = tk.Canvas(
            self.canvas_container,
            width=canvas_width,
            height=canvas_height,
            bg=COLOR_BG,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER
        )
        self.canvas.pack(anchor="center", expand=True)

        # Create rectangle items for each grid cell and cache their canvas IDs
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLOR_EMPTY,
                    outline=COLOR_GRID_LINE,
                    width=1
                )
                self.cell_rect_ids[(r, c)] = rect_id

        # Bind Mouse Events
        self.canvas.bind("<Button-1>", self._on_canvas_left_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_left_drag)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<B3-Motion>", self._on_canvas_right_drag)

    def _pos_from_event(self, event) -> Optional[Coord]:
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    def _on_canvas_left_click(self, event):
        if self.is_running:
            return
        pos = self._pos_from_event(event)
        if not pos:
            return

        tool = self.tool_var.get()
        if tool == "start":
            if pos != self.goal_pos and self.grid[pos[0]][pos[1]] == 0:
                self.start_pos = pos
                self._update_all_cells()
        elif tool == "goal":
            if pos != self.start_pos and self.grid[pos[0]][pos[1]] == 0:
                self.goal_pos = pos
                self._update_all_cells()
        elif tool == "erase":
            self._set_cell(pos, 0)
        else:  # tool == "wall"
            if pos != self.start_pos and pos != self.goal_pos:
                self._set_cell(pos, 1)

    def _on_canvas_left_drag(self, event):
        if self.is_running:
            return
        pos = self._pos_from_event(event)
        if not pos:
            return

        tool = self.tool_var.get()
        if tool == "wall" and pos != self.start_pos and pos != self.goal_pos:
            self._set_cell(pos, 1)
        elif tool == "erase" and pos != self.start_pos and pos != self.goal_pos:
            self._set_cell(pos, 0)

    def _on_canvas_right_click(self, event):
        if self.is_running:
            return
        pos = self._pos_from_event(event)
        if pos and pos != self.start_pos and pos != self.goal_pos:
            self._set_cell(pos, 0)

    def _on_canvas_right_drag(self, event):
        if self.is_running:
            return
        pos = self._pos_from_event(event)
        if pos and pos != self.start_pos and pos != self.goal_pos:
            self._set_cell(pos, 0)

    def _set_cell(self, pos: Coord, val: int):
        r, c = pos
        self.grid[r][c] = val
        color = COLOR_WALL if val == 1 else COLOR_EMPTY
        self.canvas.itemconfig(self.cell_rect_ids[pos], fill=color)

    def _update_all_cells(self):
        """Redraws the entire grid based on walls, start, goal, visited, and path."""
        path_set = set(self.path_cells)
        for r in range(self.rows):
            for c in range(self.cols):
                pos = (r, c)
                rect_id = self.cell_rect_ids[pos]
                
                if pos == self.start_pos:
                    self.canvas.itemconfig(rect_id, fill=COLOR_START)
                elif pos == self.goal_pos:
                    self.canvas.itemconfig(rect_id, fill=COLOR_GOAL)
                elif pos in path_set:
                    self.canvas.itemconfig(rect_id, fill=COLOR_PATH)
                elif self.grid[r][c] == 1:
                    self.canvas.itemconfig(rect_id, fill=COLOR_WALL)
                elif pos in self.visited_cells:
                    self.canvas.itemconfig(rect_id, fill=COLOR_CLOSED)
                else:
                    self.canvas.itemconfig(rect_id, fill=COLOR_EMPTY)

    def clear_path_visuals(self):
        """Clears search paths and visited nodes while keeping walls, start, and goal."""
        self.is_running = False
        self.generator = None
        self.visited_cells.clear()
        self.path_cells.clear()
        self.lbl_status.config(text="Status: Cleared Path", foreground="#cdd6f4")
        self.lbl_visited.config(text="Visited Nodes: 0")
        self.lbl_length.config(text="Path Cost: -")
        self.lbl_time.config(text="Time: 0 ms")
        self._update_all_cells()

    def clear_all(self):
        """Clears all walls and search visuals."""
        self.is_running = False
        self.generator = None
        self.grid = generate_blank_grid(self.rows, self.cols)
        self.visited_cells.clear()
        self.path_cells.clear()
        self.lbl_status.config(text="Status: Grid Cleared", foreground="#cdd6f4")
        self.lbl_visited.config(text="Visited Nodes: 0")
        self.lbl_length.config(text="Path Cost: -")
        self.lbl_time.config(text="Time: 0 ms")
        self._update_all_cells()

    def generate_backtracker_maze(self):
        """Generates a structured recursive maze."""
        self.clear_path_visuals()
        self.grid = generate_recursive_backtracker_maze(
            self.rows, self.cols, self.start_pos, self.goal_pos
        )
        self._update_all_cells()
        self.lbl_status.config(text="Status: Generated Recursive Maze", foreground=COLOR_ACCENT)

    def generate_random_obstacles(self):
        """Generates random obstacle scatter."""
        self.clear_path_visuals()
        self.grid = generate_random_walls(
            self.rows, self.cols, density=0.30,
            start=self.start_pos, goal=self.goal_pos
        )
        self._update_all_cells()
        self.lbl_status.config(text="Status: Generated Random Walls", foreground=COLOR_ACCENT)

    def start_visualization(self):
        """Starts step-by-step animated A* solve."""
        if self.is_running:
            return

        self.clear_path_visuals()
        self.is_running = True
        self.search_start_time = time.perf_counter()
        self.lbl_status.config(text="Status: Searching...", foreground=COLOR_OPEN)

        heuristic = self.heuristic_var.get()
        allow_diag = self.diagonal_var.get()

        self.generator = astar_generator(
            self.grid, self.start_pos, self.goal_pos,
            heuristic_name=heuristic, allow_diagonal=allow_diag
        )
        self._animate_step()

    def _animate_step(self):
        if not self.is_running or not self.generator:
            return

        try:
            step = next(self.generator)
            
            # Update newly discovered open set cells
            for node in step.open_set:
                if node != self.start_pos and node != self.goal_pos:
                    self.canvas.itemconfig(self.cell_rect_ids[node], fill=COLOR_OPEN)
            
            # Update closed set cells
            for node in step.closed_set:
                if node != self.start_pos and node != self.goal_pos:
                    self.canvas.itemconfig(self.cell_rect_ids[node], fill=COLOR_CLOSED)
            
            # Highlight current focus node
            if step.current != self.start_pos and step.current != self.goal_pos:
                self.canvas.itemconfig(self.cell_rect_ids[step.current], fill=COLOR_CURRENT)

            self.visited_cells = set(step.closed_set)
            self.lbl_visited.config(text=f"Visited Nodes: {len(self.visited_cells)}")

            if step.is_done:
                elapsed_ms = (time.perf_counter() - self.search_start_time) * 1000
                self.lbl_time.config(text=f"Time: {elapsed_ms:.1f} ms")
                self.is_running = False
                
                if step.found:
                    self.path_cells = step.path
                    self._highlight_path(step.path)
                    cost = step.g_score.get(self.goal_pos, len(step.path) - 1)
                    self.lbl_status.config(text="Status: Path Found! 🎉", foreground="#2ed573")
                    self.lbl_length.config(text=f"Path Cost: {cost:.2f} ({len(step.path)} steps)")
                else:
                    self.lbl_status.config(text="Status: No Path Found! 🚫", foreground="#ff4757")
                    self.lbl_length.config(text="Path Cost: Infinite")
                return

            delay = max(1, self.speed_var.get())
            self.root.after(delay, self._animate_step)

        except StopIteration:
            self.is_running = False

    def _highlight_path(self, path: List[Coord]):
        """Highlights the reconstructed shortest path."""
        for node in path:
            if node != self.start_pos and node != self.goal_pos:
                self.canvas.itemconfig(self.cell_rect_ids[node], fill=COLOR_PATH)

    def step_visualization(self):
        """Advances search by a single step."""
        if not self.generator:
            self.clear_path_visuals()
            self.search_start_time = time.perf_counter()
            heuristic = self.heuristic_var.get()
            allow_diag = self.diagonal_var.get()
            self.generator = astar_generator(
                self.grid, self.start_pos, self.goal_pos,
                heuristic_name=heuristic, allow_diagonal=allow_diag
            )
            self.lbl_status.config(text="Status: Stepping...", foreground=COLOR_OPEN)

        try:
            step = next(self.generator)
            for node in step.open_set:
                if node != self.start_pos and node != self.goal_pos:
                    self.canvas.itemconfig(self.cell_rect_ids[node], fill=COLOR_OPEN)
            for node in step.closed_set:
                if node != self.start_pos and node != self.goal_pos:
                    self.canvas.itemconfig(self.cell_rect_ids[node], fill=COLOR_CLOSED)
            if step.current != self.start_pos and step.current != self.goal_pos:
                self.canvas.itemconfig(self.cell_rect_ids[step.current], fill=COLOR_CURRENT)

            self.visited_cells = set(step.closed_set)
            self.lbl_visited.config(text=f"Visited Nodes: {len(self.visited_cells)}")

            if step.is_done:
                elapsed_ms = (time.perf_counter() - self.search_start_time) * 1000
                self.lbl_time.config(text=f"Time: {elapsed_ms:.1f} ms")
                self.generator = None
                if step.found:
                    self.path_cells = step.path
                    self._highlight_path(step.path)
                    cost = step.g_score.get(self.goal_pos, len(step.path) - 1)
                    self.lbl_status.config(text="Status: Path Found! 🎉", foreground="#2ed573")
                    self.lbl_length.config(text=f"Path Cost: {cost:.2f} ({len(step.path)} steps)")
                else:
                    self.lbl_status.config(text="Status: No Path Found! 🚫", foreground="#ff4757")
                    self.lbl_length.config(text="Path Cost: Infinite")

        except StopIteration:
            self.generator = None

    def solve_instant(self):
        """Solves instantly without step-by-step animation."""
        self.clear_path_visuals()
        heuristic = self.heuristic_var.get()
        allow_diag = self.diagonal_var.get()

        t0 = time.perf_counter()
        path, visited, cost = astar_solve(
            self.grid, self.start_pos, self.goal_pos,
            heuristic_name=heuristic, allow_diagonal=allow_diag
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        self.visited_cells = visited
        self.lbl_visited.config(text=f"Visited Nodes: {len(visited)}")
        self.lbl_time.config(text=f"Time: {elapsed_ms:.2f} ms")

        # Color visited cells
        for node in visited:
            if node != self.start_pos and node != self.goal_pos:
                self.canvas.itemconfig(self.cell_rect_ids[node], fill=COLOR_CLOSED)

        if path:
            self.path_cells = path
            self._highlight_path(path)
            self.lbl_status.config(text="Status: Path Found! 🎉", foreground="#2ed573")
            self.lbl_length.config(text=f"Path Cost: {cost:.2f} ({len(path)} steps)")
        else:
            self.lbl_status.config(text="Status: No Path Found! 🚫", foreground="#ff4757")
            self.lbl_length.config(text="Path Cost: Infinite")

    def stop_visualization(self):
        """Stops running animation."""
        self.is_running = False
        self.lbl_status.config(text="Status: Paused / Stopped", foreground="#f39c12")
