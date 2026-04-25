"""
A* pathfinding service — 2D grid implementation.

Mirrors the lab-style A* (sorted list frontier, explicit g/came_from dicts)
adapted for a 2-D grid instead of an explicit graph.

Lab → Grid mapping
------------------
  graph[node].items()   →  4 adjacent cells (up/down/left/right), computed on the fly
  edge cost             →  cost of entering the neighbour cell (ROAD=1, ROAD_TRAFFIC=3)
  heuristic[node]       →  heuristic(current, end) computed on the fly

Public API
----------
astar_steps(grid, heuristic_name) -> Generator[tuple[grid, type_str, message], None, None]

Message types
-------------
  "info"   — algorithm started
  "step"   — one node explored
  "done"   — path found; grid has PATH overlay
  "error"  — no path reachable, or invalid grid
"""

from __future__ import annotations

import math
from typing import Generator

from utils.grid_utils import (
    IMPASSABLE,
    START,
    END,
    TRAVERSAL_COST,
    find_cell,
    clone_grid,
    build_visual_grid,
    build_path_grid,
)

# ── Type aliases ──────────────────────────────────────────────────────────────
Grid      = list[list[int]]
Node      = tuple[int, int]          # (row, col)
StepYield = tuple[Grid, str, str]    # (visual_grid, msg_type, message)

# 4-directional movement: up, down, left, right
_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ── Heuristics ────────────────────────────────────────────────────────────────

def _manhattan(a: Node, b: Node) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _euclidean(a: Node, b: Node) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def _diagonal(a: Node, b: Node) -> float:
    """Chebyshev distance — diagonal moves cost 1."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

_HEURISTICS = {
    "manhattan": _manhattan,
    "euclidean": _euclidean,
    "diagonal":  _diagonal,
}


# ── Public generator ──────────────────────────────────────────────────────────

def astar_steps(
    grid: Grid,
    heuristic_name: str = "manhattan",
) -> Generator[StepYield, None, None]:
    """
    Lab-style A* on a 2-D grid.
    Yields (visual_grid, type, message) after each node is explored so the
    WebSocket handler can stream step-by-step updates to the frontend.
    """
    h    = _HEURISTICS.get(heuristic_name, _manhattan)
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    start = find_cell(grid, START)
    end   = find_cell(grid, END)

    if start is None or end is None:
        yield clone_grid(grid), "error", "Could not find the ambulance (start) or hospital (end) on the grid."
        return

    # ── Lab-style data structures ─────────────────────────────────────────────
    # frontier holds (node, f_cost) pairs — sorted manually each iteration
    frontier:  list[tuple[Node, float]] = [(start, 0 + h(start, end))]
    visited:   set[Node]                = set()          # closed set
    g_costs:   dict[Node, float]        = {start: 0}    # cheapest known cost to reach each node
    came_from: dict[Node, Node | None]  = {start: None} # for path reconstruction

    yield clone_grid(grid), "info", (
        f"A* started — ambulance at {start}, hospital at {end}. "
        f"Heuristic: {heuristic_name}. Grid: {rows}×{cols}."
    )

    while frontier:
        # Sort by f(n) = g(n) + h(n) — same as the lab
        frontier.sort(key=lambda x: x[1])
        current, current_f = frontier.pop(0)

        if current in visited:
            continue

        visited.add(current)

        g     = g_costs[current]
        h_val = h(current, end)

        # ── Goal check ────────────────────────────────────────────────────────
        if current == end:
            # Reconstruct path by walking came_from backwards (same as lab)
            path  = []
            node  = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            path_grid = build_path_grid(grid, path)
            yield path_grid, "done", (
                f"Hospital reached! 🏥  Path: {len(path)} cells. "
                f"Total cost: {g:.1f}. Explored: {len(visited)} cells."
            )
            return

        # ── Visual snapshot for this step ─────────────────────────────────────
        open_nodes = {node for node, _ in frontier}
        visual     = build_visual_grid(grid, visited, open_nodes, current)

        yield visual, "step", (
            f"Exploring ({current[0]}, {current[1]}) — "
            f"g={g:.1f}, h={h_val:.1f}, f={current_f:.1f}. "
            f"Frontier: {len(frontier)} nodes. Visited: {len(visited)} cells."
        )

        # ── Expand neighbours (replaces graph[current].items()) ───────────────
        for dr, dc in _DIRECTIONS:
            nr, nc   = current[0] + dr, current[1] + dc
            neighbour: Node = (nr, nc)

            # Bounds check
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue

            # Skip impassable cells (walls, empty) and already-visited nodes
            if grid[nr][nc] in IMPASSABLE or neighbour in visited:
                continue

            # Edge cost = cost of entering the neighbour cell (replaces graph edge weight)
            move_cost = TRAVERSAL_COST.get(grid[nr][nc], 1.0)
            new_g     = g_costs[current] + move_cost
            f_cost    = new_g + h(neighbour, end)

            # Only update if we found a cheaper path (same condition as lab)
            if neighbour not in g_costs or new_g < g_costs[neighbour]:
                g_costs[neighbour]   = new_g
                came_from[neighbour] = current
                frontier.append((neighbour, f_cost))

    yield clone_grid(grid), "error", (
        "No path found. 🚧 "
        "The hospital may be surrounded by walls or unreachable from the ambulance."
    )
