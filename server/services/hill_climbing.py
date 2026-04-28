"""
Hill Climbing (Local Search) pathfinding service — 2D grid implementation.

Mirrors the lab-style Simple Hill Climbing (first-improvement variant) adapted
for a 2-D grid path-cost optimisation problem.

Lab → Grid mapping
------------------
  state            →  complete valid path from START to END (list of cells)
  calculate_conflicts  →  _path_cost(): sum of TRAVERSAL_COST for every cell
  get_neighbors    →  _get_neighbours(): single-cell-swap while keeping adjacency
  break on first   →  first-improvement: move to the first neighbour with lower cost

On local optimum (no improvement found):
  - Log the stuck event and restart count
  - Generate a new random path via randomised DFS (random restart)
  - Continue until max_iterations is exhausted
  - Always return the BEST path seen across all restarts

Public API
----------
hill_climbing_steps(grid, max_iterations) -> Generator[tuple[grid, type_str, message], None, None]

Message types
-------------
  "info"   — algorithm started, initial path shown
  "step"   — one iteration completed (improved / stuck / restarted)
  "done"   — best path found; grid has PATH overlay
  "error"  — no path reachable, or invalid grid
"""

from __future__ import annotations

import random
from collections import deque
from typing import Generator

from utils.grid_utils import (
    IMPASSABLE,
    START,
    END,
    PATH,
    CURRENT,
    TRAVERSAL_COST,
    find_cell,
    clone_grid,
    build_path_grid,
)

# ── Type aliases ───────────────────────────────────────────────────────────────
Grid      = list[list[int]]
Node      = tuple[int, int]        # (row, col)
StepYield = tuple[Grid, str, str]  # (visual_grid, msg_type, message)

# 4-directional movement: up, down, left, right
_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ── Path helpers ───────────────────────────────────────────────────────────────

def _path_cost(grid: Grid, path: list[Node]) -> float:
    """Sum of traversal costs for every cell in the path (analogous to calculate_conflicts)."""
    return sum(TRAVERSAL_COST.get(grid[r][c], 1.0) for r, c in path)


def _adjacent(a: Node, b: Node) -> bool:
    """True if two cells are exactly one step apart (4-connectivity)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


# ── Initial path (BFS — deterministic, finds shortest) ────────────────────────

def _bfs_path(
    grid: Grid, start: Node, end: Node, rows: int, cols: int
) -> list[Node] | None:
    """Standard BFS — used for the very first path and as a DFS fallback."""
    queue: deque[tuple[Node, list[Node]]] = deque([(start, [start])])
    seen: set[Node] = {start}
    while queue:
        current, path = queue.popleft()
        if current == end:
            return path
        for dr, dc in _DIRECTIONS:
            nr, nc = current[0] + dr, current[1] + dc
            nb: Node = (nr, nc)
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and nb not in seen
                and grid[nr][nc] not in IMPASSABLE
            ):
                seen.add(nb)
                queue.append((nb, path + [nb]))
    return None


# ── Random path (iterative DFS — avoids Python recursion limit) ───────────────

def _random_dfs_path(
    grid: Grid, start: Node, end: Node, rows: int, cols: int
) -> list[Node] | None:
    """
    Iterative random DFS with backtracking.
    Produces a different (often longer) path than BFS, enabling genuine restarts.
    Iterative to avoid Python's default recursion limit on large grids.
    """
    start_dirs = list(_DIRECTIONS)
    random.shuffle(start_dirs)
    # Stack frame: (current_cell, shuffled_directions_list, next_direction_index)
    stack: list[tuple[Node, list[tuple[int, int]], int]] = [(start, start_dirs, 0)]
    path: list[Node] = [start]
    visited: set[Node] = {start}

    while stack:
        current, dirs, dir_idx = stack[-1]

        # ── Goal reached ──────────────────────────────────────────────────────
        if current == end:
            return list(path)

        # ── All directions from this cell exhausted → backtrack ───────────────
        if dir_idx >= len(dirs):
            stack.pop()
            if len(path) > 1:
                cell = path.pop()
                visited.discard(cell)
            continue

        # Advance direction index for the next visit to this frame
        stack[-1] = (current, dirs, dir_idx + 1)

        dr, dc = dirs[dir_idx]
        nr, nc = current[0] + dr, current[1] + dc
        nb: Node = (nr, nc)

        if (
            0 <= nr < rows
            and 0 <= nc < cols
            and nb not in visited
            and grid[nr][nc] not in IMPASSABLE
        ):
            visited.add(nb)
            path.append(nb)
            new_dirs = list(_DIRECTIONS)
            random.shuffle(new_dirs)
            stack.append((nb, new_dirs, 0))

    return None  # no path found from this random walk


# ── Neighbour generation ───────────────────────────────────────────────────────

def _get_neighbours(
    grid: Grid, path: list[Node], rows: int, cols: int
) -> list[list[Node]]:
    """
    Single-cell-swap neighbours (analogous to get_neighbors in the lab).

    For each intermediate cell path[i] (not start or end):
      - Try replacing it with each of its 4 adjacent cells N
      - N is valid only if:
          1. N is in bounds
          2. N is traversable (not in IMPASSABLE)
          3. N is adjacent to path[i-1]  ← preserves path connectivity
          4. N is adjacent to path[i+1]  ← preserves path connectivity
          5. N is not already in the path ← prevents cycles

    The neighbours list is shuffled so first-improvement doesn't always
    favour the same direction.
    """
    neighbours: list[list[Node]] = []
    path_set: set[Node] = set(path)

    for i in range(1, len(path) - 1):
        prev_cell = path[i - 1]
        next_cell = path[i + 1]

        for dr, dc in _DIRECTIONS:
            nr, nc = path[i][0] + dr, path[i][1] + dc
            new_cell: Node = (nr, nc)

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if grid[nr][nc] in IMPASSABLE:
                continue
            if new_cell == path[i]:
                continue
            if not _adjacent(prev_cell, new_cell) or not _adjacent(new_cell, next_cell):
                continue
            if new_cell in path_set:
                continue

            new_path = path[:i] + [new_cell] + path[i + 1:]
            neighbours.append(new_path)

    random.shuffle(neighbours)  # randomise order so first-improvement explores evenly
    return neighbours


# ── Visual grid builder ───────────────────────────────────────────────────────

def _build_path_visual(
    grid: Grid, path: list[Node], highlight: Node | None = None
) -> Grid:
    """
    Build a visual grid showing the current candidate path.
    Optionally mark one cell as CURRENT (the cell just swapped this iteration).
    """
    visual = clone_grid(grid)
    protected = {START, END}

    for r, c in path:
        if visual[r][c] not in protected:
            visual[r][c] = PATH

    if highlight and visual[highlight[0]][highlight[1]] not in protected:
        visual[highlight[0]][highlight[1]] = CURRENT

    return visual


# ── Public generator ───────────────────────────────────────────────────────────

def hill_climbing_steps(
    grid: Grid,
    max_iterations: int = 1000,
) -> Generator[StepYield, None, None]:
    """
    Random-restart simple hill climbing on a 2-D grid.

    State      = complete valid path from START → END (list of Nodes)
    Cost       = sum of TRAVERSAL_COST[cell] for every cell in the path
    Neighbour  = path with one intermediate cell swapped (adjacency preserved)
    Strategy   = first-improvement: move to the FIRST neighbour with lower cost
    On stuck   = random restart via randomised DFS; always track global best
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    start = find_cell(grid, START)
    end   = find_cell(grid, END)

    if start is None or end is None:
        yield clone_grid(grid), "error", (
            "Could not find the ambulance (start) or hospital (end) on the grid."
        )
        return

    # ── Build initial path with BFS ───────────────────────────────────────────
    initial_path = _bfs_path(grid, start, end, rows, cols)
    if initial_path is None:
        yield clone_grid(grid), "error", (
            "No traversable path exists between the ambulance and hospital. "
            "The map may be completely blocked by walls."
        )
        return

    current_path = initial_path
    current_cost = _path_cost(grid, current_path)

    best_path = list(current_path)
    best_cost = current_cost

    restart_count  = 0
    improved_count = 0
    # Only stream a visual frame every N improvements to cap total frames at ~50.
    # Stuck / restart events are always streamed regardless.
    step_interval = max(1, max_iterations // 50)

    yield _build_path_visual(grid, current_path), "info", (
        f"━━━ HILL CLIMBING STARTED ━━━\n"
        f"  Start (Ambulance) : {start}\n"
        f"  End   (Hospital)  : {end}\n"
        f"  Grid              : {rows} × {cols}\n"
        f"  Max iterations    : {max_iterations}\n"
        f"  Initial path      : {len(current_path)} cells\n"
        f"  Initial cost      : {current_cost:.1f}\n"
        f"  (cost = sum of cell traversal weights along path)"
    )

    # ── Main loop ─────────────────────────────────────────────────────────────
    for iteration in range(1, max_iterations + 1):

        neighbours = _get_neighbours(grid, current_path, rows, cols)

        # ── First-improvement search (mirrors lab's break-on-first-better) ────
        moved      = False
        swapped_at: Node | None = None

        for nb_path in neighbours:
            nb_cost = _path_cost(grid, nb_path)
            if nb_cost < current_cost:
                # Find which cell changed so we can highlight it
                for idx, (old_c, new_c) in enumerate(zip(current_path, nb_path)):
                    if old_c != new_c:
                        swapped_at = new_c
                        break

                improvement   = current_cost - nb_cost
                current_path  = nb_path
                current_cost  = nb_cost
                improved_count += 1
                moved = True

                if current_cost < best_cost:
                    best_cost = current_cost
                    best_path = list(current_path)

                # Only emit a visual frame every step_interval improvements
                if improved_count % step_interval == 0:
                    yield _build_path_visual(grid, current_path, swapped_at), "step", (
                        f"[Iter {iteration:>{len(str(max_iterations))}}/{max_iterations}]  ✅  IMPROVED"
                        f" (#{improved_count})\n"
                        f"  Action          : Swapped cell → {swapped_at}\n"
                        f"  Current cost    : {current_cost:.1f}  (saved {improvement:.1f})\n"
                        f"  Best cost so far: {best_cost:.1f}\n"
                        f"  Path length     : {len(current_path)} cells\n"
                        f"  Neighbours found: {len(neighbours)}\n"
                        f"  Total restarts  : {restart_count}"
                    )
                break  # ← first-improvement: stop checking neighbours

        if not moved:
            # ── Stuck at local optimum ────────────────────────────────────────
            restart_count += 1

            yield _build_path_visual(grid, current_path), "step", (
                f"[Iter {iteration:>{len(str(max_iterations))}}/{max_iterations}]  ⚠️  LOCAL OPTIMUM — STUCK\n"
                f"  Current cost    : {current_cost:.1f}\n"
                f"  Best cost so far: {best_cost:.1f}\n"
                f"  Path length     : {len(current_path)} cells\n"
                f"  Neighbours found: {len(neighbours)}  (none improved)\n"
                f"  ➜ Random restart #{restart_count} triggered..."
            )

            # ── Random restart ────────────────────────────────────────────────
            new_path = _random_dfs_path(grid, start, end, rows, cols)
            if new_path is None:
                new_path = _bfs_path(grid, start, end, rows, cols)

            if new_path is not None:
                current_path = new_path
                current_cost = _path_cost(grid, current_path)

                yield _build_path_visual(grid, current_path), "step", (
                    f"[Iter {iteration:>{len(str(max_iterations))}}/{max_iterations}]  🔄  RESTARTED  (#{restart_count})\n"
                    f"  New path length : {len(current_path)} cells\n"
                    f"  New path cost   : {current_cost:.1f}\n"
                    f"  Best cost so far: {best_cost:.1f}\n"
                    f"  Improvements so far: {improved_count}"
                )

    # ── Done — report global best ─────────────────────────────────────────────
    final_grid = build_path_grid(grid, best_path)
    yield final_grid, "done", (
        f"━━━ HILL CLIMBING COMPLETE ━━━\n"
        f"  Best path length    : {len(best_path)} cells\n"
        f"  Best path cost      : {best_cost:.1f}\n"
        f"  Total iterations    : {max_iterations}\n"
        f"  Total improvements  : {improved_count}\n"
        f"  Total restarts      : {restart_count}\n"
        f"  Outcome             : {'Optimal local solution' if restart_count == 0 else f'Best of {restart_count + 1} restarts'}"
    )
