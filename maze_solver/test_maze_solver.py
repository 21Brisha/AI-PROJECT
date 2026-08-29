"""
Unit tests and verification script for A* Maze Solver.
"""

import unittest
from astar import astar_solve, astar_generator, HEURISTICS
from maze_generator import (
    generate_blank_grid,
    generate_random_walls,
    generate_recursive_backtracker_maze
)

class TestAStarMazeSolver(unittest.TestCase):
    def test_straight_line_path(self):
        grid = generate_blank_grid(10, 10)
        start = (1, 1)
        goal = (1, 5)
        path, visited, cost = astar_solve(grid, start, goal, "Manhattan", allow_diagonal=False)
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 5)
        self.assertEqual(cost, 4.0)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

    def test_wall_obstacle_navigation(self):
        grid = generate_blank_grid(5, 5)
        # Create a vertical wall dividing the grid with one opening
        grid[1][2] = 1
        grid[2][2] = 1
        grid[3][2] = 1
        # Leave (4, 2) and (0, 2) open
        start = (2, 0)
        goal = (2, 4)
        path, visited, cost = astar_solve(grid, start, goal, "Manhattan", allow_diagonal=False)
        self.assertIsNotNone(path)
        self.assertIn(start, path)
        self.assertIn(goal, path)
        # Verify no path node goes through walls
        for r, c in path:
            self.assertEqual(grid[r][c], 0)

    def test_unreachable_goal(self):
        grid = generate_blank_grid(5, 5)
        # Enclose goal with walls
        goal = (4, 4)
        grid[3][4] = 1
        grid[4][3] = 1
        grid[3][3] = 1
        start = (0, 0)
        path, visited, cost = astar_solve(grid, start, goal, "Manhattan", allow_diagonal=False)
        self.assertIsNone(path)

    def test_diagonal_movement(self):
        grid = generate_blank_grid(5, 5)
        start = (0, 0)
        goal = (3, 3)
        path_diag, _, cost_diag = astar_solve(grid, start, goal, "Euclidean", allow_diagonal=True)
        path_orth, _, cost_orth = astar_solve(grid, start, goal, "Manhattan", allow_diagonal=False)
        self.assertIsNotNone(path_diag)
        self.assertIsNotNone(path_orth)
        self.assertLess(cost_diag, cost_orth)

    def test_generator_yields_done(self):
        grid = generate_blank_grid(6, 6)
        start = (0, 0)
        goal = (2, 2)
        gen = astar_generator(grid, start, goal, "Manhattan")
        steps = list(gen)
        self.assertTrue(len(steps) > 0)
        last_step = steps[-1]
        self.assertTrue(last_step.is_done)
        self.assertTrue(last_step.found)
        self.assertEqual(last_step.path[0], start)
        self.assertEqual(last_step.path[-1], goal)

    def test_maze_generators(self):
        rows, cols = 15, 15
        start, goal = (1, 1), (13, 13)
        
        # Test random generator
        random_grid = generate_random_walls(rows, cols, 0.25, start, goal)
        self.assertEqual(len(random_grid), rows)
        self.assertEqual(len(random_grid[0]), cols)
        self.assertEqual(random_grid[start[0]][start[1]], 0)
        self.assertEqual(random_grid[goal[0]][goal[1]], 0)

        # Test recursive backtracker
        backtracker_grid = generate_recursive_backtracker_maze(rows, cols, start, goal)
        self.assertEqual(len(backtracker_grid), rows)
        self.assertEqual(len(backtracker_grid[0]), cols)
        self.assertEqual(backtracker_grid[start[0]][start[1]], 0)
        self.assertEqual(backtracker_grid[goal[0]][goal[1]], 0)

if __name__ == "__main__":
    unittest.main()
