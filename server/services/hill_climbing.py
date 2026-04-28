"""
Hill Climbing (Local Search) pathfinding service — 2D grid implementation.

Mirrors the lab-style Simple Hill Climbing (first-improvement variant) adapted
for a 2-D grid path-cost optimisation problem.

Lab → Grid mapping
------------------
  state            →  complete valid path from START to END (list of cells)
  calculate_conflicts  →  _path_cost(): sum of TRAVERSAL_COST for every cell
  get_neighbors    →  _get_neighbours(): segment-replacement (pick two path indices,
                       find alt BFS route between them avoiding current segment)
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


# ── Random path (randomised BFS — always finds a path, always different) ─────

def _random_bfs_path(
    grid: Grid, start: Node, end: Node, rows: int, cols: int
) -> list[Node] | None:
    """
    Randomised BFS for random restarts.

    Shuffles the neighbour list before enqueuing at every expansion, so each
    call explores the grid in a different order and produces a genuinely
    different path.  Unlike the old random-walk DFS, BFS always finds a path
    when one exists — it never gets stuck — so the BFS fallback is unnecessary.
    """
    queue: deque[tuple[Node, list[Node]]] = deque([(start, [start])])
    seen: set[Node] = {start}
    while queue:
        current, path = queue.popleft()
        dirs = list(_DIRECTIONS)
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = current[0] + dr, current[1] + dc
            nb: Node = (nr, nc)
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and nb not in seen
                and grid[nr][nc] not in IMPASSABLE
            ):
                seen.add(nb)
                new_path = path + [nb]
                if nb == end:
                    return new_path
                queue.append((nb, new_path))
    return None



# ── BFS with exclusion set (used by segment-replacement neighbours) ───────────

def _bfs_avoiding(
    grid: Grid,
    start: Node,
    end: Node,
    rows: int,
    cols: int,
    excluded: set[Node],
) -> list[Node] | None:
    """
    Standard BFS that treats every cell in *excluded* as impassable.
    The start and end cells are never blocked even if present in the set.
    """
    if start == end:
        return [start]
    queue: deque[tuple[Node, list[Node]]] = deque([(start, [start])])
    seen: set[Node] = {start}
    while queue:
        current, path = queue.popleft()
        for dr, dc in _DIRECTIONS:
            nr, nc = current[0] + dr, current[1] + dc
            nb: Node = (nr, nc)
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and nb not in seen
                and nb not in excluded
                and grid[nr][nc] not in IMPASSABLE
            ):
                seen.add(nb)
                new_path = path + [nb]
                if nb == end:
                    return new_path
                queue.append((nb, new_path))
    return None


# ── Neighbour generation ───────────────────────────────────────────────────────

def _get_neighbours(
    grid: Grid, path: list[Node], rows: int, cols: int
) -> list[list[Node]]:
    """
    Segment-replacement neighbours.

    Samples random index pairs (i, j) with i < j from the path and finds an
    alternative BFS route between path[i] and path[j] that avoids:
      - the current segment interior  path[i+1 .. j-1]  (forces a detour)
      - all other cells already in the path              (prevents cycles)

    This is essential for large grids: the old single-cell-swap required the
    replacement cell to be adjacent to BOTH its neighbours in the path, which
    is only possible at bends.  A BFS shortest path is mostly straight, so
    the old approach returned zero valid neighbours immediately and the
    algorithm was permanently stuck after the first iteration.
    """
    if len(path) <= 2:
        return []

    neighbours: list[list[Node]] = []
    path_len = len(path)

    # Scale the number of segment pairs tried with path length
    num_samples = min(60, max(20, path_len // 2))
    tried: set[tuple[int, int]] = set()
    attempts = 0

    while attempts < num_samples * 4 and len(neighbours) < num_samples:
        attempts += 1

        i = random.randint(0, path_len - 3)
        # Prefer shorter segments (higher chance of alt route) but allow longer
        max_j = min(path_len - 1, i + max(4, path_len // 5))
        j = random.randint(i + 2, max_j)

        if (i, j) in tried:
            continue
        tried.add((i, j))

        # Cells the alternative must avoid to prevent re-using the current
        # segment or creating a cycle with the rest of the path
        segment_interior = set(path[i + 1:j])
        other_path_cells  = (set(path[:i]) | set(path[j + 1:])) - {path[i], path[j]}
        excluded = segment_interior | other_path_cells

        alt = _bfs_avoiding(grid, path[i], path[j], rows, cols, excluded)
        if alt is None or alt == path[i:j + 1]:
            continue

        new_path = path[:i] + alt + path[j + 1:]
        neighbours.append(new_path)

    random.shuffle(neighbours)
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
    Neighbour  = path with one segment replaced by an alternative BFS route
    Strategy   = first-improvement: move to the FIRST neighbour with lower cost
    On stuck   = random restart via randomised BFS; always track global best
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
            new_path = _random_bfs_path(grid, start, end, rows, cols)
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
