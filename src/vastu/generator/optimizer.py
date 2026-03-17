"""Space optimizer maximizing usable area while maintaining Vastu compliance.

Uses iterative refinement to expand rooms into available space and improve
both utilization and Vastu scores.
"""

from __future__ import annotations

import numpy as np

from vastu.models import Direction, FloorPlan, Room, RoomType
from vastu.vastu_rules.compliance import VastuComplianceChecker
from vastu.vastu_rules.directions import DirectionalRules


class SpaceOptimizer:
    """Optimizes floor plan layout to maximize usable area.

    Strategies:
    1. Expand rooms into adjacent empty space
    2. Adjust proportions toward golden ratio
    3. Minimize wasted corridor space
    4. Ensure Vastu compliance is maintained or improved
    """

    def __init__(self, max_iterations: int = 50):
        self.max_iterations = max_iterations
        self._checker = VastuComplianceChecker()

    def optimize(self, plan: FloorPlan) -> FloorPlan:
        """Run optimization passes on the floor plan.

        Args:
            plan: The initial floor plan to optimize.

        Returns:
            Optimized floor plan with improved space utilization.
        """
        best_plan = plan.model_copy(deep=True)
        best_score = self._evaluate(best_plan)

        for _ in range(self.max_iterations):
            candidate = best_plan.model_copy(deep=True)

            # Try expanding rooms
            candidate = self._expand_rooms(candidate)

            # Try improving proportions
            candidate = self._improve_proportions(candidate)

            candidate_score = self._evaluate(candidate)
            if candidate_score > best_score:
                best_plan = candidate
                best_score = candidate_score
            else:
                break  # No improvement, stop

        return best_plan

    def _evaluate(self, plan: FloorPlan) -> float:
        """Score a plan combining space utilization and Vastu compliance.

        Returns a composite score (0-200) where:
        - 0-100 from Vastu compliance
        - 0-100 from space utilization quality
        """
        vastu_score = self._checker.check_compliance(plan)
        util = plan.utilization

        # Utilization score: optimal is 70-80%, penalize under/over
        if 65 <= util <= 85:
            util_score = 100.0
        elif util < 65:
            util_score = max(0, util / 65 * 100)
        else:
            util_score = max(0, 100 - (util - 85) * 5)

        return vastu_score.overall_score + util_score

    def _expand_rooms(self, plan: FloorPlan) -> FloorPlan:
        """Try to expand each room into adjacent empty space."""
        expand_step = 1.0  # feet

        for i, room in enumerate(plan.rooms):
            other_rooms = [r for j, r in enumerate(plan.rooms) if j != i]

            # Try expanding width (eastward)
            expanded_w = room.width + expand_step
            if room.x + expanded_w <= plan.width:
                if not self._would_overlap(room.x, room.y, expanded_w, room.length, other_rooms):
                    plan.rooms[i] = room.model_copy(update={"width": expanded_w})
                    room = plan.rooms[i]

            # Try expanding length (northward)
            expanded_l = room.length + expand_step
            if room.y + expanded_l <= plan.length:
                if not self._would_overlap(room.x, room.y, room.width, expanded_l, other_rooms):
                    plan.rooms[i] = room.model_copy(update={"length": expanded_l})

        return plan

    def _improve_proportions(self, plan: FloorPlan) -> FloorPlan:
        """Adjust room dimensions toward more balanced proportions."""
        golden_ratio = 1.618

        for i, room in enumerate(plan.rooms):
            ratio = max(room.width, room.length) / min(room.width, room.length)

            if ratio > 2.0:
                # Room is too elongated, try to balance
                other_rooms = [r for j, r in enumerate(plan.rooms) if j != i]

                if room.width > room.length:
                    # Try reducing width, increasing length
                    new_w = room.width - 0.5
                    new_l = room.length + 0.5
                else:
                    new_w = room.width + 0.5
                    new_l = room.length - 0.5

                if new_w > 0 and new_l > 0:
                    if (room.x + new_w <= plan.width and
                            room.y + new_l <= plan.length and
                            not self._would_overlap(room.x, room.y, new_w, new_l, other_rooms)):
                        plan.rooms[i] = room.model_copy(update={"width": new_w, "length": new_l})

        return plan

    def _would_overlap(
        self, x: float, y: float, w: float, l: float, others: list[Room],
    ) -> bool:
        """Check if a rectangle would overlap with any other rooms."""
        for room in others:
            if (x < room.x + room.width and x + w > room.x and
                    y < room.y + room.length and y + l > room.y):
                return True
        return False

    def get_utilization_report(self, plan: FloorPlan) -> dict:
        """Generate a report on space utilization."""
        total = plan.total_area
        used = plan.used_area
        unused = total - used

        room_areas = {}
        for room in plan.rooms:
            rtype = room.room_type.value
            room_areas[rtype] = room_areas.get(rtype, 0) + room.area

        return {
            "total_plot_area_sqft": round(total, 1),
            "used_area_sqft": round(used, 1),
            "unused_area_sqft": round(unused, 1),
            "utilization_pct": round(plan.utilization, 1),
            "area_by_room_type": {k: round(v, 1) for k, v in room_areas.items()},
        }
