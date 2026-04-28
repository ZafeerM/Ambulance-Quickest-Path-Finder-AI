"""
Genetic Algorithm pathfinding service — 2D grid implementation.

Mirrors the lab-style Genetic Algorithm (hospital duty scheduling) adapted for
2-D grid path-cost optimisation.

Lab → Grid mapping
------------------
  chromosome (staff × shifts matrix)  →  valid path from START → END (list of cells)
  evaluate_fitness(schedule)           →  _path_cost(): sum of TRAVERSAL_COST per cell
  create_random_schedule()             →  _random_path(): randomised DFS (BFS fallback)
  select_parents() — top 50%          →  sort population by cost, keep top half
  crossover() — single-point on cols  →  splice parent1-prefix + parent2-suffix at a
                                          shared intermediate cell
  mutate() — swap two shifts           →  re-route a random sub-segment via random DFS

Public API
----------
genetic_steps(grid, population_size, generations, mutation_rate)
    -> Generator[tuple[grid, type_str, message], None, None]

Message types
-------------
  "info"   — algorithm started, initial-best path shown
  "step"   — one generation completed (current best path overlaid on grid)
  "done"   — evolution finished; grid has PATH overlay for best-ever path
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
    VISITED,
    FRONTIER,
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

_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ── Path helpers ───────────────────────────────────────────────────────────────

def _path_cost(grid: Grid, path: list[Node]) -> float:
    """
    Sum of traversal costs for every cell in the path.
    Analogous to evaluate_fitness(schedule) in the lab — lower score = better.
    """
    return sum(TRAVERSAL_COST.get(grid[r][c], 1.0) for r, c in path)


def _bfs_path(
    grid: Grid, start: Node, end: Node, rows: int, cols: int
) -> list[Node] | None:
    """Standard BFS — deterministic shortest path, used as fallback."""
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


def _random_dfs_path(
    grid: Grid, start: Node, end: Node, rows: int, cols: int
) -> list[Node] | None:
    """
    Random walk WITHOUT backtracking — O(N) guaranteed.

    At each step, picks a random unvisited traversable neighbour.
    If no unvisited neighbour exists the walk is stuck and returns None;
    the caller falls back to BFS.

    The old backtracking DFS removed cells from 'visited' when unwinding,
    allowing exponential re-exploration on fully open grids — this caused
    the server to hang indefinitely on obstacle-free maps.
    Analogous to create_random_schedule() in the lab.
    """
    visited: set[Node] = {start}
    path: list[Node] = [start]
    current = start

    while current != end:
        neighbours: list[Node] = []
        for dr, dc in _DIRECTIONS:
            nr, nc = current[0] + dr, current[1] + dc
            nb: Node = (nr, nc)
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and nb not in visited
                and grid[nr][nc] not in IMPASSABLE
            ):
                neighbours.append(nb)

        if not neighbours:
            return None  # stuck — caller falls back to BFS

        random.shuffle(neighbours)
        nxt = neighbours[0]
        visited.add(nxt)
        path.append(nxt)
        current = nxt

    return path


def _make_path(grid: Grid, start: Node, end: Node, rows: int, cols: int) -> list[Node] | None:
    """Random DFS first for diversity; BFS fallback if DFS fails."""
    p = _random_dfs_path(grid, start, end, rows, cols)
    return p if p is not None else _bfs_path(grid, start, end, rows, cols)


# ── GA operators ───────────────────────────────────────────────────────────────

def _crossover(
    parent1: list[Node],
    parent2: list[Node],
) -> list[Node] | None:
    """
    Single-point crossover at a randomly chosen shared intermediate cell.

    Analogous to the lab's:
        point = random.randint(0, num_shifts - 1)
        child = [parent1[i][:point] + parent2[i][point:] for i in range(num_staff)]

    Here the "crossover point" is a cell that appears in both paths
    (excluding the endpoints, which are always shared).

    child = parent1[:idx1 + 1]  +  parent2[idx2 + 1:]

    Returns None if no eligible shared cell exists (caller falls back to a copy
    of one of the parents).
    """
    set1 = set(parent1)
    # Eligible shared cells: exclude start and end (always equal) so the
    # resulting child is meaningfully different from either parent.
    shared = [
        cell for cell in parent2
        if cell in set1 and cell != parent1[0] and cell != parent1[-1]
    ]
    if not shared:
        return None

    splice = random.choice(shared)
    idx1 = parent1.index(splice)
    idx2 = parent2.index(splice)

    child = parent1[: idx1 + 1] + parent2[idx2 + 1 :]

    # Reject the child if it contains duplicate cells (i.e. a cycle formed)
    if len(child) != len(set(child)):
        return None

    return child


def _mutate(
    path: list[Node],
    grid: Grid,
    rows: int,
    cols: int,
) -> list[Node]:
    """
    Re-route a random intermediate sub-segment via random DFS.

    Analogous to the lab's:
        staff  = random.randint(0, num_staff - 1)
        shift1, shift2 = random.sample(range(num_shifts), 2)
        schedule[staff][shift1], schedule[staff][shift2] = (
            schedule[staff][shift2], schedule[staff][shift1]
        )

    Here: pick two random intermediate indices i < j, then replace
    path[i : j+1] with a freshly generated path from path[i] to path[j].
    Falls back to the original path when re-routing fails.
    """
    if len(path) <= 3:
        return path  # too short to mutate meaningfully

    indices = list(range(1, len(path) - 1))
    if len(indices) < 2:
        return path

    i, j = sorted(random.sample(indices, 2))
    seg_start = path[i]
    seg_end   = path[j]

    new_seg = _random_dfs_path(grid, seg_start, seg_end, rows, cols)
    if new_seg is None:
        new_seg = _bfs_path(grid, seg_start, seg_end, rows, cols)
    if new_seg is None:
        return path  # segment is impassable, keep original

    mutated = path[:i] + new_seg + path[j + 1 :]

    # Reject if cycles were introduced
    if len(mutated) != len(set(mutated)):
        return path

    return mutated


# ── Visual builders ───────────────────────────────────────────────────────────

def _build_cloud_grid(
    grid: Grid,
    population: list[list[Node]],
    best_path: list[Node],
    pop_size: int,
    champion_color: int | None = CURRENT,
) -> Grid:
    """
    Build a frequency-heat overlay for the entire population.

    Frequency tiers (drawn bottom → top so hotter layers always win):
      any path visited          →  VISITED  (grey  — explored zone)
      ≥ 50 % of paths           →  FRONTIER (orange — convergence zone)
      champion (if requested)   →  champion_color (purple during steps,
                                                    omitted on the info frame)
      START / END never overwritten.

    Pass champion_color=None to suppress the champion overlay (gen 0 info frame).
    Pass champion_color=CURRENT for step frames (purple = still evolving).
    The done frame uses build_path_grid directly so PATH (pink) only appears there.
    """
    freq: dict[Node, int] = {}
    for path in population:
        for cell in path:
            freq[cell] = freq.get(cell, 0) + 1

    visual        = clone_grid(grid)
    protected     = {START, END}
    hot_threshold = pop_size * 0.5

    # Layer 1 — cool zone: any cell touched by at least one path
    for (r, c), _ in freq.items():
        if visual[r][c] not in protected:
            visual[r][c] = VISITED

    # Layer 2 — hot zone: cells shared by ≥ 50 % of paths
    for (r, c), count in freq.items():
        if count >= hot_threshold and visual[r][c] not in protected:
            visual[r][c] = FRONTIER

    # Layer 3 — champion: drawn only when a color is specified
    if champion_color is not None:
        for r, c in best_path:
            if visual[r][c] not in protected:
                visual[r][c] = champion_color

    return visual


def _progress_bar(gen: int, total: int, width: int = 20) -> str:
    """Return an ASCII progress bar string, e.g. '[████░░░░░░░░░░░░░░░░]  20.0%'."""
    filled = round(gen / total * width) if total > 0 else 0
    bar    = "█" * filled + "░" * (width - filled)
    pct    = gen / total * 100 if total > 0 else 0.0
    return f"[{bar}] {pct:5.1f}%"


# ── Public generator ───────────────────────────────────────────────────────────

def genetic_steps(
    grid: Grid,
    population_size: int = 100,
    generations: int = 200,
    mutation_rate: float = 0.05,
) -> Generator[StepYield, None, None]:
    """
    Genetic Algorithm on a 2-D grid.

    Chromosome = valid path (list of cells) from START to END.
    Fitness    = total traversal cost — lower is better (mirrors lab's penalty score).
    Selection  = elitist top-50% (same strategy as the lab).
    Crossover  = single-point splice at a shared intermediate cell.
    Mutation   = re-route a random sub-segment.

    Streams one frame per generation showing the current best-ever path.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    start = find_cell(grid, START)
    end   = find_cell(grid, END)

    if start is None or end is None:
        yield clone_grid(grid), "error", (
            "Could not find ambulance (start) or hospital (end) on the grid."
        )
        return

    # Verify that at least one path exists before building the population
    if _bfs_path(grid, start, end, rows, cols) is None:
        yield clone_grid(grid), "error", (
            "No traversable path exists. The ambulance is completely surrounded by walls."
        )
        return

    # ── Step 1 (lab): Initialise population ────────────────────────────────────
    # Analogous to: population = [create_random_schedule() for _ in range(population_size)]
    population: list[list[Node]] = []
    while len(population) < population_size:
        p = _make_path(grid, start, end, rows, cols)
        if p is not None:
            population.append(p)

    fitness_scores = [_path_cost(grid, p) for p in population]
    best_idx  = fitness_scores.index(min(fitness_scores))
    best_path = list(population[best_idx])
    best_cost = fitness_scores[best_idx]

    gen_width = len(str(generations))  # for zero-padded log messages

    # Count hot cells (shared by ≥50% of the initial population)
    init_freq: dict[Node, int] = {}
    for path in population:
        for cell in path:
            init_freq[cell] = init_freq.get(cell, 0) + 1
    init_hot = sum(1 for c in init_freq.values() if c >= population_size * 0.5)

    # Gen-0 info frame: show only the initial population cloud — no champion
    # overlay yet, so the pink final-answer colour is never shown from frame 0.
    yield _build_cloud_grid(grid, population, best_path, population_size, champion_color=None), "info", (
        f"🧬 GENETIC ALGORITHM — GEN 0 / {generations}\n"
        f"   {_progress_bar(0, generations)}\n"
        f"   Start  : {start}   End  : {end}   Grid : {rows}×{cols}\n"
        f"   Pop    : {population_size} paths   Mutation : {mutation_rate * 100:.0f}%\n"
        f"   ▶ Initial best cost : {best_cost:.1f}   ({len(best_path)} cells)\n"
        f"   🔵 Explored cloud : {len(init_freq)} cells   🟠 Converging : {init_hot} cells"
    )

    # ── Steps 2-5 (lab): Evolve ────────────────────────────────────────────────
    for generation in range(1, generations + 1):

        # ── Step 2: Evaluate fitness ───────────────────────────────────────────
        # Analogous to: fitness_scores = [evaluate_fitness(s) for s in population]
        fitness_scores = [_path_cost(grid, p) for p in population]
        gen_best_cost  = min(fitness_scores)

        # Track global best across all generations
        gen_best_idx = fitness_scores.index(gen_best_cost)
        if gen_best_cost < best_cost:
            best_cost = gen_best_cost
            best_path = list(population[gen_best_idx])
            marker = "✅"
        else:
            marker = "  "

        # ── Step 3: Selection — top 50% ────────────────────────────────────────
        # Analogous to: parents = select_parents(population, fitness_scores)
        paired   = sorted(zip(fitness_scores, population), key=lambda x: x[0])
        parents  = [p for _, p in paired[: len(population) // 2]]

        # ── Build next generation via crossover + mutation ─────────────────────
        new_population: list[list[Node]] = []

        while len(new_population) < population_size:
            parent1, parent2 = random.sample(parents, 2)

            # ── Step 4: Crossover ──────────────────────────────────────────────
            # Analogous to: child = crossover(parent1, parent2)
            child = _crossover(parent1, parent2)
            if child is None:
                # No shared intermediate cell — clone a parent instead
                child = list(random.choice([parent1, parent2]))

            # ── Step 5: Mutate ─────────────────────────────────────────────────
            # Analogous to: child = mutate(child)  (applied with probability)
            if random.random() < mutation_rate:
                child = _mutate(child, grid, rows, cols)

            new_population.append(child)

        population = new_population

        # Build cloud stats for the log
        cloud_freq: dict[Node, int] = {}
        for path in population:
            for cell in path:
                cloud_freq[cell] = cloud_freq.get(cell, 0) + 1
        cloud_size  = len(cloud_freq)
        hot_cells   = sum(1 for cnt in cloud_freq.values() if cnt >= population_size * 0.5)
        improve_tag = "✅ IMPROVED!" if marker == "✅" else "·"

        # Stream one frame per generation — cloud + champion in purple (CURRENT).
        # Purple signals "best so far, still evolving"; pink (PATH) only on done.
        yield _build_cloud_grid(grid, population, best_path, population_size, champion_color=CURRENT), "step", (
            f"🧬 GENETIC ALGORITHM — GEN {generation:{gen_width}} / {generations}   {improve_tag}\n"
            f"   {_progress_bar(generation, generations)}\n"
            f"   Gen best cost    : {gen_best_cost:.1f}\n"
            f"   Overall best     : {best_cost:.1f}   ({len(best_path)} cells)\n"
            f"   🔵 Cloud : {cloud_size} cells   🟠 Converging : {hot_cells} cells   Parents : {len(parents)}"
        )

    # ── Done — overlay the best-ever path ──────────────────────────────────────
    final_grid = build_path_grid(grid, best_path)
    yield final_grid, "done", (
        f"🧬 GENETIC ALGORITHM COMPLETE\n"
        f"   {_progress_bar(generations, generations)}\n"
        f"   ✅ Best path length : {len(best_path)} cells\n"
        f"   ✅ Best path cost   : {best_cost:.1f}\n"
        f"   Generations run    : {generations}\n"
        f"   Population size    : {population_size}\n"
        f"   Mutation rate      : {mutation_rate * 100:.0f}%"
    )
