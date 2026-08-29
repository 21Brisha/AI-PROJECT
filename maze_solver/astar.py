"""
A* Pathfinding Algorithm Implementation
Supports 4-directional and 8-directional movement, custom heuristics,
and both batch solving and step-by-step generator for UI visualization.
"""

import heapq
import math
from typing import List, Tuple, Dict, Set, Optional, Generator, Callable

# Coordinate representation: (row, col)
Coord = Tuple[int, int]

# Heuristic functions
def manhattan_distance(a: Coord, b: Coord) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean_distance(a: Coord, b: Coord) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def chebyshev_distance(a: Coord, b: Coord) -> float:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def octile_distance(a: Coord, b: Coord) -> float:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)

HEURISTICS: Dict[str, Callable[[Coord, Coord], float]] = {
    "Manhattan": manhattan_distance,
    "Euclidean": euclidean_distance,
    "Chebyshev": chebyshev_distance,
    "Octile": octile_distance
}

def get_neighbors(pos: Coord, rows: int, cols: int, allow_diagonal: bool = False) -> List[Tuple[Coord, float]]:
    """Returns accessible adjacent coordinates and movement costs."""
    r, c = pos
    # 4 cardinal directions (cost 1.0)
    directions = [
        ((-1, 0), 1.0),
        ((1, 0), 1.0),
        ((0, -1), 1.0),
        ((0, 1), 1.0)
    ]
    
    if allow_diagonal:
        # 4 diagonal directions (cost sqrt(2) ~ 1.414)
        diag_cost = math.sqrt(2)
        directions.extend([
            ((-1, -1), diag_cost),
            ((-1, 1), diag_cost),
            ((1, -1), diag_cost),
            ((1, 1), diag_cost)
        ])
        
    neighbors = []
    for (dr, dc), cost in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            neighbors.append(((nr, nc), cost))
            
    return neighbors

def reconstruct_path(came_from: Dict[Coord, Coord], current: Coord) -> List[Coord]:
    """Reconstructs the path from start to current node."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

class AStarStep:
    """Represents a state yielded during step-by-step search."""
    def __init__(self, current: Coord, open_set: Set[Coord], closed_set: Set[Coord], 
                 came_from: Dict[Coord, Coord], g_score: Dict[Coord, float],
                 is_done: bool = False, path: Optional[List[Coord]] = None,
                 found: bool = False):
        self.current = current
        self.open_set = open_set
        self.closed_set = closed_set
        self.came_from = came_from
        self.g_score = g_score
        self.is_done = is_done
        self.path = path or []
        self.found = found

def astar_generator(
    grid: List[List[int]], 
    start: Coord, 
    goal: Coord, 
    heuristic_name: str = "Manhattan",
    allow_diagonal: bool = False
) -> Generator[AStarStep, None, None]:
    """
    Generator that yields the search state at each exploration step for live animation.
    grid: 0 for empty cell, 1 for obstacle/wall.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    heuristic_fn = HEURISTICS.get(heuristic_name, manhattan_distance)
    
    # Priority queue: entries are (f_score, counter, coord)
    counter = 0
    open_heap = []
    heapq.heappush(open_heap, (heuristic_fn(start, goal), counter, start))
    
    open_set_coords: Set[Coord] = {start}
    closed_set: Set[Coord] = set()
    
    came_from: Dict[Coord, Coord] = {}
    g_score: Dict[Coord, float] = {start: 0.0}
    f_score: Dict[Coord, float] = {start: heuristic_fn(start, goal)}
    
    while open_heap:
        current_f, _, current = heapq.heappop(open_heap)
        
        if current not in open_set_coords:
            continue
            
        open_set_coords.remove(current)
        closed_set.add(current)
        
        # Check if reached goal
        if current == goal:
            path = reconstruct_path(came_from, current)
            yield AStarStep(current, open_set_coords, closed_set, came_from, g_score, is_done=True, path=path, found=True)
            return
            
        # Yield current step
        yield AStarStep(current, open_set_coords, closed_set, came_from, g_score, is_done=False)
        
        # Explore neighbors
        for neighbor, move_cost in get_neighbors(current, rows, cols, allow_diagonal):
            nr, nc = neighbor
            if grid[nr][nc] == 1:  # Obstacle
                continue
                
            # Prevent cutting through diagonal walls if moving diagonally
            if allow_diagonal and abs(nr - current[0]) == 1 and abs(nc - current[1]) == 1:
                # If both adjacent orthogonal cells are walls, cannot squeeze through
                if grid[current[0]][nc] == 1 and grid[nr][current[1]] == 1:
                    continue
            
            tentative_g = g_score[current] + move_cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_val = tentative_g + heuristic_fn(neighbor, goal)
                f_score[neighbor] = f_val
                
                if neighbor not in open_set_coords and neighbor not in closed_set:
                    counter += 1
                    heapq.heappush(open_heap, (f_val, counter, neighbor))
                    open_set_coords.add(neighbor)
                elif neighbor in open_set_coords:
                    # Re-add with updated lower f_score
                    counter += 1
                    heapq.heappush(open_heap, (f_val, counter, neighbor))
                    
    # No path found
    yield AStarStep(start, open_set_coords, closed_set, came_from, g_score, is_done=True, path=[], found=False)

def astar_solve(
    grid: List[List[int]], 
    start: Coord, 
    goal: Coord, 
    heuristic_name: str = "Manhattan",
    allow_diagonal: bool = False
) -> Tuple[Optional[List[Coord]], Set[Coord], float]:
    """
    Direct solver returning (path, visited_nodes, total_cost).
    """
    generator = astar_generator(grid, start, goal, heuristic_name, allow_diagonal)
    last_step = None
    for step in generator:
        last_step = step
        
    if last_step and last_step.found:
        total_cost = last_step.g_score.get(goal, 0.0)
        return last_step.path, last_step.closed_set, total_cost
        
    closed = last_step.closed_set if last_step else set()
    return None, closed, 0.0
