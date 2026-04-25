from __future__ import annotations

# ---------------------------------------------------------------------------
# Grid value constants — must stay in sync with client/src/constants/cellTypes.js
# ---------------------------------------------------------------------------

# ── Original cell types (sent FROM the frontend) ──
EMPTY        = 0   # internal only — non-traversable, never placed by the user
ROAD         = 1
OBSTACLE     = 2   # default cell (wall)
START        = 3
END          = 4
ROAD_TRAFFIC = 5   # road with heavy traffic — traversable but high cost

# ── Overlay values added by the server during pathfinding ──
# Start at 10 to leave room for future cell types (values 1-9).
# These are streamed BACK to the frontend so it can colour each state.
VISITED  = 10  # closed set  — already fully explored
FRONTIER = 11  # open set    — discovered but not yet explored
CURRENT  = 12  # the node being processed in the current step
PATH     = 13  # cells that form the final reconstructed path

# Cells that block movement — EMPTY is also impassable (can never be drawn)
IMPASSABLE = {OBSTACLE, EMPTY}

# Movement cost per cell type (lower = preferred)
TRAVERSAL_COST: dict[int, float] = {
    ROAD:         1.0,   # ideal path
    ROAD_TRAFFIC: 3.0,   # slow — AI avoids if a cleaner route exists
    START:        0.0,   # free
    END:          0.0,   # free
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clone_grid(grid: list[list[int]]) -> list[list[int]]:
    """Return a shallow row-copy of a 2-D integer grid."""
    return [row[:] for row in grid]


def find_cell(grid: list[list[int]], value: int) -> tuple[int, int] | None:
    """Return the (row, col) of the first cell matching *value*, or None."""
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == value:
                return (r, c)
    return None


def reconstruct_path(
    came_from: dict[tuple[int, int], tuple[int, int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Walk *came_from* backwards from *end* to *start* and return the ordered path."""
    path: list[tuple[int, int]] = []
    node = end
    while node in came_from:
        path.append(node)
        node = came_from[node]
    path.append(start)
    path.reverse()
    return path


def build_visual_grid(
    base_grid: list[list[int]],
    closed_set: set[tuple[int, int]],
    open_set: set[tuple[int, int]],
    current: tuple[int, int] | None = None,
) -> list[list[int]]:
    """
    Overlay pathfinding state on a copy of *base_grid*.
    Original START / END cells are never overwritten so they stay visible.
    """
    visual = clone_grid(base_grid)
    protected = {START, END}

    for node in closed_set:
        if visual[node[0]][node[1]] not in protected:
            visual[node[0]][node[1]] = VISITED

    for node in open_set:
        if visual[node[0]][node[1]] not in protected:
            visual[node[0]][node[1]] = FRONTIER

    if current and visual[current[0]][current[1]] not in protected:
        visual[current[0]][current[1]] = CURRENT

    return visual


def build_path_grid(
    base_grid: list[list[int]],
    path: list[tuple[int, int]],
) -> list[list[int]]:
    """Return a copy of *base_grid* with PATH overlay on all path cells."""
    result = clone_grid(base_grid)
    protected = {START, END}
    for node in path:
        if result[node[0]][node[1]] not in protected:
            result[node[0]][node[1]] = PATH
    return result
