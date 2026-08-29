"""
Maze Generation Module
Provides algorithms to procedurally generate mazes:
1. Recursive Backtracking (Perfect maze with labyrinth corridors)
2. Random Obstacle Distribution (Configurable density)
"""

import random
from typing import List, Tuple

Coord = Tuple[int, int]

def generate_blank_grid(rows: int, cols: int) -> List[List[int]]:
    """Returns a grid filled with 0s (empty cells)."""
    return [[0 for _ in range(cols)] for _ in range(rows)]

def generate_random_walls(rows: int, cols: int, density: float = 0.28,
                          start: Coord = (0, 0), goal: Coord = (0, 0)) -> List[List[int]]:
    """
    Generates a grid where cells are randomly turned into walls with probability `density`.
    Ensures start and goal are always empty.
    """
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if (r, c) == start or (r, c) == goal:
                grid[r][c] = 0
            else:
                grid[r][c] = 1 if random.random() < density else 0
    return grid

def generate_recursive_backtracker_maze(rows: int, cols: int, 
                                        start: Coord = (0, 0), 
                                        goal: Coord = (0, 0)) -> List[List[int]]:
    """
    Generates a classic maze using the Recursive Backtracker (DFS) algorithm.
    Creates structured, winding passageways and dead ends.
    """
    # Start with a grid of all walls
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    
    # We carve paths at odd coordinates (1, 3, 5, ...)
    # Adjust start/carve origin to fit odd cell indexing
    start_r = 1 if rows > 2 else 0
    start_c = 1 if cols > 2 else 0
    
    grid[start_r][start_c] = 0
    stack = [(start_r, start_c)]
    visited = {(start_r, start_c)}
    
    # Carve maze
    while stack:
        cr, cc = stack[-1]
        
        # 2-step neighbors (up, down, left, right)
        neighbors = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = cr + dr, cc + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                if (nr, nc) not in visited:
                    neighbors.append((nr, nc, dr // 2, dc // 2))
                    
        if neighbors:
            nr, nc, wall_dr, wall_dc = random.choice(neighbors)
            # Remove wall between current and chosen neighbor
            grid[cr + wall_dr][cc + wall_dc] = 0
            grid[nr][nc] = 0
            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()
            
    # Guarantee start and goal cells are cleared and connected
    sr, sc = start
    gr, gc = goal
    grid[sr][sc] = 0
    grid[gr][gc] = 0
    
    # Connect start to nearest open corridor if walled in
    _ensure_connected_to_passage(grid, sr, sc, rows, cols)
    # Connect goal to nearest open corridor if walled in
    _ensure_connected_to_passage(grid, gr, gc, rows, cols)
    
    return grid

def _ensure_connected_to_passage(grid: List[List[int]], r: int, c: int, rows: int, cols: int):
    """Helper to ensure start/goal has at least one adjacent open passage."""
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            grid[nr][nc] = 0
            break
