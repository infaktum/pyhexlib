from __future__ import annotations

from typing import List, Tuple

import pyhexlib
from pyhexlib import basic as b
from pyhexlib.basic import Direction, Hexagon, Orientation, Neighborhood, Bounds


# ----------------------------------- Hexagon Generation -----------------------------------

def rectangle_map(rows: int, cols: int) -> List[Hexagon]:
    return [Hexagon(row, col) for col in range(cols) for row in range(rows)]


# ----------------------------------- HexagonalGrid -----------------------------------

class HexagonalGrid:

    def __init__(self, hexagons: List[Hexagon]) -> None:
        self.hexagons = hexagons

    # --------------------------- Methods dependent from Orientation -------------------------------

    @staticmethod
    def _offset_to_axial(row: int, col: int) -> Direction:
        return b.offset_to_axial(row, col)

    @staticmethod
    def _axial_to_offset(r: int, q: int) -> Tuple[int, int]:
        return b.axial_to_offset(r, q)

    @staticmethod
    def _neighborhood(rc: Hexagon) -> List[Hexagon]:
        return b.neighborhood_basic(*rc)

    # -----------------------------------  Properties -------------------------------

    @property
    def size(self) -> tuple[int, int]:
        (r_min, c_min), (r_max, c_max) = self.bounds.topleft, self.bounds.bottomright
        rows, cols = (r_max + 1) - r_min, (c_max + 1) - c_min
        width, height = cols, rows
        return height, width

    @property
    def bounds(self) -> Bounds:
        rs = [rc[0] for rc in self.hexagons]
        cs = [rc[1] for rc in self.hexagons]
        r_min, r_max = min(rs), max(rs)
        c_min, c_max = min(cs), max(cs)
        return Bounds(r_min, c_min, r_max, c_max)

    @property
    def axial_coordinates(self):
        return {(r, c): self._offset_to_axial(r, c) for (r, c) in self.hexagons}

    # ----------------------------------- Methods -------------------------------

    def get_distance(self, rc1: Hexagon, rc2: Hexagon) -> int:
        return b.distance_axial(self._offset_to_axial(*rc1), self._offset_to_axial(*rc2))

    @staticmethod
    def get_direction(start: Hexagon, end: Hexagon) -> Direction:
        """
        Returns the direction from start to end as one of the constants NORTH, NORTHEAST, etc.
        If end is not a direct neighbor of start, returns None.
        """
        return b.get_direction(start, end)

    def get_direction_(self, rc1: Hexagon, rc2: Hexagon) -> Direction:
        """
        Returns the direction from rc1 to rc2 as one of the constants NORTH, NORTHEAST, etc.
        If rc2 is not a direct neighbor of rc1, return the approximate direction (closest of the six).
        If rc1 == rc2, returns None.
        """
        # first try exact neighbor lookup (parity-aware offset)
        direct = self.get_direction(rc1, rc2)

        if direct is not None:
            return direct

        # convert offset -> axial -> cube
        ax1 = b.offset_to_axial(*rc1)
        ax2 = b.offset_to_axial(*rc2)

        c1 = b.axial_to_cube(ax1)
        c2 = b.axial_to_cube(ax2)
        diff = (c2[0] - c1[0], c2[1] - c1[1], c2[2] - c1[2])

        # identical cell
        if diff == (0, 0, 0):
            return None

        # build candidate unit vectors from the six direct neighbors of rc1
        candidates = []
        for nb in self._neighborhood(rc1):
            ax_nb = b.offset_to_axial(*nb)
            c_nb = b.axial_to_cube(ax_nb)
            vec = (c_nb[0] - c1[0], c_nb[1] - c1[1], c_nb[2] - c1[2])
            # dot product between diff and unit neighbor vector
            dot = diff[0] * vec[0] + diff[1] * vec[1] + diff[2] * vec[2]
            # map this neighbor vector back to a Direction using the same parity mapping
            direction = b.neighborhood_basic(nb[1] - rc1[1], nb[0] - rc1[0])
            if direction is not None:
                candidates.append((dot, direction))

        if not candidates:
            return None

        # choose the direction with the largest dot product (closest angle)
        best = max(candidates, key=lambda t: t[0])
        return best[1]

    # -------------------------------- Python Container Methods -------------------------------

    def __iter__(self):
        return iter(self.hexagons)

    def __len__(self) -> int:
        return len(self.hexagons)

    def __contains__(self, item) -> bool:
        return item in self.hexagons

    # ----------------------------------- Neighbors-----------------------------------

    def neighbors(self, rc: Hexagon, dist: int = 1, max_cost: int = None, cost_fn=None, ) -> List[Hexagon]:
        if cost_fn is None:
            return self._neighbors_without_cost(rc, dist)
        else:
            return list(self._neighbors_with_cost(rc, max_cost, cost_fn=cost_fn, dist=dist).keys())

    # neighbors without cost function, for internal use (e.g. to find neighbors of a planet for highlighting)

    def _neighbors_without_cost(self, rc: Hexagon, dist: int = 1) -> List[Hexagon]:
        """
        Finds all direct neighbors of a hexagon at rc = (row, col) in `hexagons`.

        :return: List of (row, col) of neighbors in `hexagons`
        """
        if dist == 1:
            return [nb for nb in self._neighborhood(rc) if nb in self.hexagons]
        else:
            return self._neighbors(rc, dist)

    def _neighbors(self, rc: Tuple[int, int], dist: int) -> List[Tuple[int, int]]:
        """
        Gibt alle Hexes aus `hexagons` zurück, deren Abstand zu `hex` maximal `dist` ist.
        `hexagons` und `hex` sind Offset-(row, col)-Paare. Orientation kann `Orientation.FLAT` oder `Orientation.POINTY` sein.
        """
        center_ax = self._offset_to_axial(*rc)
        result: List[Tuple[int, int]] = []

        for h in [h for h in self.hexagons if h != rc]:
            cand_ax = self._offset_to_axial(*h)
            if b.distance_axial(center_ax, cand_ax) <= dist:
                result.append(h)

        return result

    # ------------------------------ Neighbors with cost function -------------------------------

    def get_neighborhood(self, rc: Hexagon, max_cost: int, cost_fn=None, dist: int = 1, ) -> Neighborhood:
        return Neighborhood(rc, self._neighbors_with_cost(rc, dist=dist, max_cost=max_cost, cost_fn=cost_fn))

    def _neighbors_with_cost(self, rc: Hexagon, max_cost: int, cost_fn=None, dist: int = 1, ) -> dict:
        """
        Sammle alle Hex-Felder, die von `start` aus mit kumulierten Bewegungskosten <= max_cost
           Rückgabe: dict: rc -> (cost, steps, prev) wobei prev das Vorgängerfeld ist (oder None für start).
        - hexagons: Container mit vorhandenen Koordinaten (z.B. dict, set, MovementGrid)
        - start: (row, col)
        - max_cost: maximale kumulierte Bewegungskosten (incl. Kosten der betretenen Felder)
        - cost_fn: optional, Funktion cost_fn(rc) -> Kosten zum Betreten von rc
        - max_steps: optional maximale Anzahl an Schritten
        - dist: Nachbarabstand, weitergegeben an `neighbors`
        """
        import heapq

        # Quick sanity check: if start is not a valid hex in our grid, there are no reachable tiles.
        if rc not in self.hexagons:
            return {}

        # We'll use a min-heap (priority queue) to expand nodes in order of lowest cumulative cost.
        # Each heap entry is a tuple with primary sort key = cum_cost, secondary = steps, then node & prev.
        # Using steps as secondary key gives a deterministic tie-breaker: fewer steps is preferred
        # when cumulative costs are equal.
        #
        # Heap entry format: (cum_cost, steps, node, prev)
        #   - cum_cost (int/float): cumulative cost from `start` to `node`
        #   - steps (int): number of steps taken from `start` to `node`
        #   - node: the coordinate tuple for the current hex (row, col)
        #   - prev: the predecessor coordinate of `node` (or None for the start)
        heap = [(0, 0, rc, None)]  # (cum_cost, steps, node, prev)

        # `best` stores the best-known record for each discovered node. Value format: (cost, steps, prev)
        # It represents the optimal (so far) cumulative cost to reach the node, the steps used, and
        # the predecessor to reconstruct a path if needed.
        best = {rc: (0, 0, None)}  # node -> (cost, steps, prev)

        # Main loop: standard Dijkstra-like expansion but with an explicit step counter and a
        # per-node record that contains the predecessor. We stop expanding any path whose
        # cumulative cost would exceed `max_cost`.
        while heap:
            cur_cost, cur_steps, cur, cur_prev = heapq.heappop(heap)

            # If the popped tuple is stale (we already found a better cost/steps for `cur`), skip it.
            # This is the usual lazy-deletion technique for priority queues without decrease-key.
            recorded = best.get(cur)
            if recorded is None or (cur_cost, cur_steps) != (recorded[0], recorded[1]):
                # The heap entry does not match the currently recorded best values for this node.
                # It means a better path was found and recorded after this entry was pushed.
                continue

            # Iterate over neighbors at the requested neighbor distance (`dist`).
            # `_neighbors` returns only coordinates that exist in `self.hexagons` and are within `dist`.
            for nb in self._neighbors(cur, dist=dist):
                # Determine the cost to enter the neighbor tile. The cost function is expected to
                # return a numeric cost, or None/inf to indicate an impassable tile.
                step_cost = cost_fn(nb)

                # If the cost function explicitly marks the tile as impassable (None or +inf), skip it.
                if step_cost is None or step_cost == float('inf'):
                    continue

                # Compute the new cumulative cost and the step count that would result from
                # moving from `cur` to `nb`.
                new_cost = cur_cost + step_cost
                new_steps = cur_steps + 1

                # If we've exceeded the allowed budget, drop this neighbor.
                # Note: `max_cost` should be a numeric value; passing None would raise a TypeError
                # when comparing. The caller should ensure `max_cost` is provided.
                if new_cost > max_cost:
                    continue

                # Get any previously recorded best value for this neighbor.
                prev_record = best.get(nb)

                # We update the neighbor's record if we found a strictly lower cumulative cost, or
                # if the cost is equal, but we reached it in fewer steps (tie-breaker).
                if (prev_record is None) or (new_cost < prev_record[0]) or (
                        new_cost == prev_record[0] and new_steps < prev_record[1]):
                    # Save the better path info: (cost, steps, predecessor)
                    best[nb] = (new_cost, new_steps, cur)

                    # Push the new candidate onto the heap for further expansion.
                    # The heap may now contain stale entries for `nb` with worse cost/steps, but
                    # those will be ignored when popped due to the recorded-check above.
                    heapq.heappush(heap, (new_cost, new_steps, nb, cur))
        # NOTE: The `best` dict maps each reachable node to a triple (cost, steps, prev).
        # - cost: the minimum cumulative cost found to reach that node (<= max_cost)
        # - steps: the number of steps used to reach the node for that cost
        # - prev: the previous node along the best path (or None for `start`)
        #
        # This structure allows callers to both query reachable nodes within the budget and to
        # reconstruct the cheapest paths by following the `prev` links back to `start`.
        return best

    # ---------------------------------- Pathfinding -------------------------------

    def path(self, rc: Hexagon, goal: Hexagon, cost_fn=None) -> List[Hexagon]:
        return b.astar(self.hexagons, rc, goal, cost_fn)
        # return b.dijkstra(self.hexagons, rc, goal, cost_fn)

    # ----------------------------------- Representation -------------------------------

    def __repr__(self) -> str:
        cnt = len(getattr(self, "hexagons", []))
        (rmin, cmin), (rmax, cmax) = self.bounds
        bounds = f"({rmin},{cmin})-({rmax},{cmax})"
        sample = list(getattr(self, "hexagons", []))[:8]
        return f"{self.__class__.__name__}(count={cnt}, bounds={bounds}, sample={sample})"


# ----------------------------------- Main Test -------------------------------------------------

if __name__ == "__main__":
    # Example usage

    pyhexlib.init(orientation=Orientation.FLAT)

    hexagons = [(row, col) for col in range(-10, 10) for row in range(-10, 10)]

    grid = HexagonalGrid(hexagons)

    start = (0, 0)

    cost_fn = lambda n: 1

    neighborhood = grid.get_neighborhood(start, dist=4, max_cost=4, cost_fn=cost_fn)
