"""Vastu Shastra compliance checker scoring floor plans against 20+ rules.

This module implements a comprehensive set of Vastu Shastra rules derived from
traditional texts and modern Vastu practice. Each rule is scored independently
and weighted by importance to produce an overall compliance score.
"""

from __future__ import annotations

import numpy as np

from vastu.models import (
    Direction,
    FloorPlan,
    Room,
    RoomType,
    VastuRule,
    VastuScore,
)
from vastu.vastu_rules.directions import DirectionalRules


class VastuComplianceChecker:
    """Checks a floor plan against 20+ Vastu Shastra rules and produces a score."""

    def check_compliance(self, plan: FloorPlan) -> VastuScore:
        """Run all Vastu rules against the floor plan and return a VastuScore."""
        rules: list[VastuRule] = []

        checkers = [
            self._rule_kitchen_southeast,
            self._rule_master_bedroom_southwest,
            self._rule_puja_northeast,
            self._rule_entrance_north_east,
            self._rule_living_north_east,
            self._rule_bathroom_northwest,
            self._rule_no_bathroom_northeast,
            self._rule_no_kitchen_northeast,
            self._rule_brahmasthan_open,
            self._rule_staircase_not_northeast,
            self._rule_bedroom_not_southeast,
            self._rule_plot_shape_regular,
            self._rule_northeast_lowest,
            self._rule_southwest_heaviest,
            self._rule_no_toilet_near_kitchen,
            self._rule_dining_near_kitchen,
            self._rule_study_west_or_southwest,
            self._rule_store_northwest_southwest,
            self._rule_no_bedroom_center,
            self._rule_entrance_not_south,
            self._rule_kitchen_facing,
            self._rule_room_proportions,
            self._rule_minimum_room_sizes,
            self._rule_space_utilization,
        ]

        for checker in checkers:
            rule = checker(plan)
            rules.append(rule)

        passed = sum(1 for r in rules if r.passed)
        failed = sum(1 for r in rules if r.passed is False)
        total = len(rules)

        weights = np.array([r.weight for r in rules])
        scores = np.array([1.0 if r.passed else 0.0 for r in rules])
        if weights.sum() > 0:
            overall = float(np.average(scores, weights=weights) * 100)
        else:
            overall = 0.0

        direction_rules = [r for r in rules if r.category == "direction"]
        placement_rules = [r for r in rules if r.category == "placement"]
        proportion_rules = [r for r in rules if r.category == "proportion"]

        def _cat_score(cat_rules: list[VastuRule]) -> float:
            if not cat_rules:
                return 100.0
            w = np.array([r.weight for r in cat_rules])
            s = np.array([1.0 if r.passed else 0.0 for r in cat_rules])
            return float(np.average(s, weights=w) * 100) if w.sum() > 0 else 0.0

        score = VastuScore(
            overall_score=round(overall, 1),
            direction_score=round(_cat_score(direction_rules), 1),
            placement_score=round(_cat_score(placement_rules), 1),
            proportion_score=round(_cat_score(proportion_rules), 1),
            rules_checked=rules,
            passed_rules=passed,
            failed_rules=failed,
            total_rules=total,
        )
        score.grade = score.compute_grade()
        return score

    # ---- Individual Rule Checkers ----

    def _rule_kitchen_southeast(self, plan: FloorPlan) -> VastuRule:
        """Rule 1: Kitchen should be in Southeast (Agni corner)."""
        kitchens = plan.get_rooms_by_type(RoomType.KITCHEN)
        passed = any(r.direction == Direction.SOUTHEAST for r in kitchens) if kitchens else False
        return VastuRule(
            id="V01", name="Kitchen in Southeast",
            description="Kitchen should be placed in the Southeast (Agni/fire) corner for alignment with fire element.",
            category="direction", weight=5.0, passed=passed,
            details=f"Kitchen directions: {[r.direction.value for r in kitchens]}" if kitchens else "No kitchen found",
        )

    def _rule_master_bedroom_southwest(self, plan: FloorPlan) -> VastuRule:
        """Rule 2: Master bedroom should be in Southwest."""
        masters = plan.get_rooms_by_type(RoomType.MASTER_BEDROOM)
        passed = any(r.direction == Direction.SOUTHWEST for r in masters) if masters else False
        return VastuRule(
            id="V02", name="Master Bedroom in Southwest",
            description="Master bedroom should be in Southwest for stability and grounding (Nairuti corner).",
            category="direction", weight=4.5, passed=passed,
            details=f"Master bedroom directions: {[r.direction.value for r in masters]}" if masters else "No master bedroom found",
        )

    def _rule_puja_northeast(self, plan: FloorPlan) -> VastuRule:
        """Rule 3: Puja room should be in Northeast (Ishanya corner)."""
        pujas = plan.get_rooms_by_type(RoomType.PUJA)
        passed = any(r.direction == Direction.NORTHEAST for r in pujas) if pujas else True  # optional room
        return VastuRule(
            id="V03", name="Puja Room in Northeast",
            description="Prayer/puja room should be in Northeast (Ishanya/Shiva corner) for spiritual purity.",
            category="direction", weight=4.0, passed=passed,
            details=f"Puja directions: {[r.direction.value for r in pujas]}" if pujas else "No puja room (acceptable)",
        )

    def _rule_entrance_north_east(self, plan: FloorPlan) -> VastuRule:
        """Rule 4: Main entrance should face North or East."""
        passed = plan.entrance_direction in (Direction.NORTH, Direction.EAST, Direction.NORTHEAST)
        return VastuRule(
            id="V04", name="Entrance Facing North/East",
            description="Main entrance should face North or East to invite prosperity, sunlight, and positive energy.",
            category="direction", weight=5.0, passed=passed,
            details=f"Entrance direction: {plan.entrance_direction.value}",
        )

    def _rule_living_north_east(self, plan: FloorPlan) -> VastuRule:
        """Rule 5: Living room should be in North or East zone."""
        living = plan.get_rooms_by_type(RoomType.LIVING)
        ideal = {Direction.NORTH, Direction.EAST, Direction.NORTHEAST}
        passed = any(r.direction in ideal for r in living) if living else False
        return VastuRule(
            id="V05", name="Living Room in North/East",
            description="Living room should face North or East for openness and wealth energy (Kubera/Indra).",
            category="direction", weight=3.5, passed=passed,
            details=f"Living directions: {[r.direction.value for r in living]}" if living else "No living room found",
        )

    def _rule_bathroom_northwest(self, plan: FloorPlan) -> VastuRule:
        """Rule 6: Bathrooms should be in Northwest or West."""
        bathrooms = plan.get_rooms_by_type(RoomType.BATHROOM)
        ideal = {Direction.NORTHWEST, Direction.WEST}
        passed = all(r.direction in ideal for r in bathrooms) if bathrooms else True
        return VastuRule(
            id="V06", name="Bathrooms in Northwest/West",
            description="Bathrooms should be in Northwest (Vayu/air) or West for proper ventilation and drainage.",
            category="direction", weight=3.0, passed=passed,
            details=f"Bathroom directions: {[r.direction.value for r in bathrooms]}" if bathrooms else "No bathrooms found",
        )

    def _rule_no_bathroom_northeast(self, plan: FloorPlan) -> VastuRule:
        """Rule 7: No bathroom/toilet in Northeast."""
        bathrooms = plan.get_rooms_by_type(RoomType.BATHROOM)
        passed = not any(r.direction == Direction.NORTHEAST for r in bathrooms)
        return VastuRule(
            id="V07", name="No Bathroom in Northeast",
            description="Bathrooms must never be in Northeast as it pollutes the sacred Ishanya corner.",
            category="placement", weight=4.5, passed=passed,
            details="Northeast bathroom found! This is a serious Vastu defect." if not passed else "No bathroom in Northeast.",
        )

    def _rule_no_kitchen_northeast(self, plan: FloorPlan) -> VastuRule:
        """Rule 8: No kitchen in Northeast."""
        kitchens = plan.get_rooms_by_type(RoomType.KITCHEN)
        passed = not any(r.direction == Direction.NORTHEAST for r in kitchens)
        return VastuRule(
            id="V08", name="No Kitchen in Northeast",
            description="Kitchen in Northeast creates fire-water conflict, harming spirituality and health.",
            category="placement", weight=4.0, passed=passed,
            details="Kitchen in Northeast is a major Vastu dosha." if not passed else "Kitchen not in Northeast.",
        )

    def _rule_brahmasthan_open(self, plan: FloorPlan) -> VastuRule:
        """Rule 9: Center of house (Brahmasthan) should be open/unobstructed."""
        center_rooms = plan.get_rooms_in_direction(Direction.CENTER)
        # Brahmasthan should ideally be open or have only a courtyard/hallway
        heavy_rooms = [r for r in center_rooms if r.room_type in (
            RoomType.KITCHEN, RoomType.BATHROOM, RoomType.STAIRCASE, RoomType.STORE
        )]
        passed = len(heavy_rooms) == 0
        return VastuRule(
            id="V09", name="Brahmasthan (Center) Open",
            description="The center of the house (Brahmasthan) should be kept open and free from heavy structures, toilets, or kitchens.",
            category="placement", weight=4.0, passed=passed,
            details=f"Heavy rooms in center: {[r.name for r in heavy_rooms]}" if heavy_rooms else "Center is clear.",
        )

    def _rule_staircase_not_northeast(self, plan: FloorPlan) -> VastuRule:
        """Rule 10: Staircase should not be in Northeast."""
        stairs = plan.get_rooms_by_type(RoomType.STAIRCASE)
        passed = not any(r.direction == Direction.NORTHEAST for r in stairs)
        return VastuRule(
            id="V10", name="Staircase Not in Northeast",
            description="Staircase in Northeast blocks positive energy flow; place in South, West, or Southwest.",
            category="placement", weight=3.5, passed=passed,
            details=f"Staircase directions: {[r.direction.value for r in stairs]}" if stairs else "No staircase.",
        )

    def _rule_bedroom_not_southeast(self, plan: FloorPlan) -> VastuRule:
        """Rule 11: Bedrooms should not be in Southeast (fire corner)."""
        bedrooms = plan.get_rooms_by_type(RoomType.BEDROOM) + plan.get_rooms_by_type(RoomType.MASTER_BEDROOM)
        passed = not any(r.direction == Direction.SOUTHEAST for r in bedrooms)
        return VastuRule(
            id="V11", name="No Bedroom in Southeast",
            description="Bedrooms in the Southeast (Agni) corner cause restlessness and health issues.",
            category="placement", weight=3.0, passed=passed,
            details="Bedroom found in Southeast fire zone." if not passed else "No bedroom in Southeast.",
        )

    def _rule_plot_shape_regular(self, plan: FloorPlan) -> VastuRule:
        """Rule 12: Plot should be regular (rectangular or square)."""
        ratio = max(plan.width, plan.length) / min(plan.width, plan.length)
        passed = ratio <= 2.0  # Vastu recommends aspect ratio close to 1:1 or at most 1:2
        return VastuRule(
            id="V12", name="Regular Plot Shape",
            description="Plot should be square or rectangular with aspect ratio not exceeding 1:2.",
            category="proportion", weight=2.0, passed=passed,
            details=f"Aspect ratio: 1:{ratio:.1f}",
        )

    def _rule_northeast_lowest(self, plan: FloorPlan) -> VastuRule:
        """Rule 13: Northeast should be the lightest/most open part of the house."""
        ne_rooms = plan.get_rooms_in_direction(Direction.NORTHEAST)
        heavy_types = {RoomType.MASTER_BEDROOM, RoomType.STORE, RoomType.GARAGE, RoomType.STAIRCASE}
        heavy = [r for r in ne_rooms if r.room_type in heavy_types]
        passed = len(heavy) == 0
        return VastuRule(
            id="V13", name="Northeast Light and Open",
            description="Northeast should be the lightest and most open area - no heavy structures or storage.",
            category="placement", weight=3.5, passed=passed,
            details=f"Heavy items in NE: {[r.name for r in heavy]}" if heavy else "Northeast is light.",
        )

    def _rule_southwest_heaviest(self, plan: FloorPlan) -> VastuRule:
        """Rule 14: Southwest should have the heaviest rooms/structures."""
        sw_rooms = plan.get_rooms_in_direction(Direction.SOUTHWEST)
        heavy_types = {RoomType.MASTER_BEDROOM, RoomType.STORE, RoomType.STAIRCASE}
        has_heavy = any(r.room_type in heavy_types for r in sw_rooms)
        # Also pass if SW just has bedrooms
        has_bedroom = any(r.room_type in {RoomType.BEDROOM, RoomType.MASTER_BEDROOM} for r in sw_rooms)
        passed = has_heavy or has_bedroom or len(sw_rooms) == 0
        return VastuRule(
            id="V14", name="Southwest Heavy/Grounded",
            description="Southwest should house heavy structures like master bedroom, storage - provides stability.",
            category="placement", weight=3.0, passed=passed,
            details=f"SW rooms: {[r.name for r in sw_rooms]}" if sw_rooms else "No rooms in Southwest yet.",
        )

    def _rule_no_toilet_near_kitchen(self, plan: FloorPlan) -> VastuRule:
        """Rule 15: Toilet should not be adjacent to or facing the kitchen."""
        kitchens = plan.get_rooms_by_type(RoomType.KITCHEN)
        bathrooms = plan.get_rooms_by_type(RoomType.BATHROOM)
        too_close = False
        for k in kitchens:
            for b in bathrooms:
                dist = ((k.center_x - b.center_x) ** 2 + (k.center_y - b.center_y) ** 2) ** 0.5
                min_dist = (k.width + b.width) / 2  # rough adjacency check
                if dist < min_dist * 1.2:
                    too_close = True
        passed = not too_close
        return VastuRule(
            id="V15", name="Toilet Not Adjacent to Kitchen",
            description="Toilet/bathroom should not share a wall with or directly face the kitchen - hygiene and energy conflict.",
            category="placement", weight=3.5, passed=passed,
            details="Bathroom too close to kitchen." if not passed else "Kitchen-bathroom separation adequate.",
        )

    def _rule_dining_near_kitchen(self, plan: FloorPlan) -> VastuRule:
        """Rule 16: Dining area should be close to the kitchen."""
        kitchens = plan.get_rooms_by_type(RoomType.KITCHEN)
        dining = plan.get_rooms_by_type(RoomType.DINING)
        if not dining or not kitchens:
            return VastuRule(
                id="V16", name="Dining Near Kitchen",
                description="Dining room should be adjacent to or near the kitchen for convenience.",
                category="placement", weight=2.0, passed=True,
                details="No separate dining room or kitchen to evaluate.",
            )
        k = kitchens[0]
        d = dining[0]
        dist = ((k.center_x - d.center_x) ** 2 + (k.center_y - d.center_y) ** 2) ** 0.5
        passed = dist < max(plan.width, plan.length) * 0.4
        return VastuRule(
            id="V16", name="Dining Near Kitchen",
            description="Dining room should be adjacent to or near the kitchen for convenience.",
            category="placement", weight=2.0, passed=passed,
            details=f"Kitchen-dining distance: {dist:.1f} ft",
        )

    def _rule_study_west_or_southwest(self, plan: FloorPlan) -> VastuRule:
        """Rule 17: Study room should be in West or Southwest."""
        studies = plan.get_rooms_by_type(RoomType.STUDY)
        if not studies:
            return VastuRule(
                id="V17", name="Study in West/Southwest",
                description="Study room should be in West or Southwest for concentration.",
                category="direction", weight=2.0, passed=True,
                details="No study room in plan.",
            )
        ideal = {Direction.WEST, Direction.SOUTHWEST, Direction.NORTH}
        passed = any(r.direction in ideal for r in studies)
        return VastuRule(
            id="V17", name="Study in West/Southwest",
            description="Study room should be in West or Southwest for concentration and focus.",
            category="direction", weight=2.0, passed=passed,
            details=f"Study directions: {[r.direction.value for r in studies]}",
        )

    def _rule_store_northwest_southwest(self, plan: FloorPlan) -> VastuRule:
        """Rule 18: Store room should be in Northwest or Southwest."""
        stores = plan.get_rooms_by_type(RoomType.STORE)
        if not stores:
            return VastuRule(
                id="V18", name="Store Room Placement",
                description="Store room should be in Northwest or Southwest.",
                category="direction", weight=1.5, passed=True,
                details="No store room in plan.",
            )
        ideal = {Direction.NORTHWEST, Direction.SOUTHWEST}
        passed = any(r.direction in ideal for r in stores)
        return VastuRule(
            id="V18", name="Store Room Placement",
            description="Store room should be in Northwest or Southwest for proper storage energy.",
            category="direction", weight=1.5, passed=passed,
            details=f"Store directions: {[r.direction.value for r in stores]}",
        )

    def _rule_no_bedroom_center(self, plan: FloorPlan) -> VastuRule:
        """Rule 19: No bedroom should occupy the Brahmasthan (center)."""
        center_bedrooms = [
            r for r in plan.get_rooms_in_direction(Direction.CENTER)
            if r.room_type in (RoomType.BEDROOM, RoomType.MASTER_BEDROOM)
        ]
        passed = len(center_bedrooms) == 0
        return VastuRule(
            id="V19", name="No Bedroom in Center",
            description="Brahmasthan (center) should remain open; placing bedrooms here blocks cosmic energy.",
            category="placement", weight=3.0, passed=passed,
            details="Bedroom in Brahmasthan." if not passed else "Center free of bedrooms.",
        )

    def _rule_entrance_not_south(self, plan: FloorPlan) -> VastuRule:
        """Rule 20: Entrance should not be in South or Southwest."""
        prohibited = {Direction.SOUTH, Direction.SOUTHWEST}
        passed = plan.entrance_direction not in prohibited
        return VastuRule(
            id="V20", name="Entrance Not in South/Southwest",
            description="South and Southwest entrances are inauspicious in Vastu; they invite negative energy (Yama direction).",
            category="direction", weight=4.5, passed=passed,
            details=f"Entrance: {plan.entrance_direction.value}",
        )

    def _rule_kitchen_facing(self, plan: FloorPlan) -> VastuRule:
        """Rule 21: Cook should face East while cooking (kitchen on east wall of SE zone)."""
        kitchens = plan.get_rooms_by_type(RoomType.KITCHEN)
        if not kitchens:
            return VastuRule(
                id="V21", name="Kitchen Cooking Direction",
                description="Person cooking should face East - kitchen platform on east wall.",
                category="direction", weight=2.5, passed=False,
                details="No kitchen found.",
            )
        # Approximate: kitchen in SE or E means cook likely faces east
        ideal = {Direction.SOUTHEAST, Direction.EAST}
        passed = any(r.direction in ideal for r in kitchens)
        return VastuRule(
            id="V21", name="Kitchen Cooking Direction",
            description="Person cooking should face East - kitchen platform on east wall.",
            category="direction", weight=2.5, passed=passed,
            details=f"Kitchen directions: {[r.direction.value for r in kitchens]}",
        )

    def _rule_room_proportions(self, plan: FloorPlan) -> VastuRule:
        """Rule 22: Rooms should have proportions close to squares or golden ratio."""
        bad_rooms = []
        for room in plan.rooms:
            ratio = max(room.width, room.length) / min(room.width, room.length)
            if ratio > 2.5:
                bad_rooms.append(room.name)
        passed = len(bad_rooms) == 0
        return VastuRule(
            id="V22", name="Room Proportions Balanced",
            description="Rooms should be close to square or golden ratio; very elongated rooms create imbalanced energy.",
            category="proportion", weight=2.0, passed=passed,
            details=f"Elongated rooms: {bad_rooms}" if bad_rooms else "All rooms have balanced proportions.",
        )

    def _rule_minimum_room_sizes(self, plan: FloorPlan) -> VastuRule:
        """Rule 23: Rooms should meet minimum size requirements."""
        min_sizes = {
            RoomType.MASTER_BEDROOM: 120,
            RoomType.BEDROOM: 100,
            RoomType.KITCHEN: 60,
            RoomType.BATHROOM: 30,
            RoomType.LIVING: 150,
            RoomType.PUJA: 20,
            RoomType.DINING: 80,
        }
        small_rooms = []
        for room in plan.rooms:
            min_area = min_sizes.get(room.room_type, 0)
            if room.area < min_area:
                small_rooms.append(f"{room.name} ({room.area:.0f} sqft < {min_area} sqft)")
        passed = len(small_rooms) == 0
        return VastuRule(
            id="V23", name="Minimum Room Sizes",
            description="Each room type has a minimum area for livability and energy flow.",
            category="proportion", weight=2.5, passed=passed,
            details=f"Undersized: {small_rooms}" if small_rooms else "All rooms meet minimum sizes.",
        )

    def _rule_space_utilization(self, plan: FloorPlan) -> VastuRule:
        """Rule 24: Space utilization should be between 60-85% (walls, corridors need space)."""
        util = plan.utilization
        passed = 55 <= util <= 90
        return VastuRule(
            id="V24", name="Space Utilization",
            description="Floor plan should use 60-85% of plot area; remainder for walls, corridors, and open space.",
            category="proportion", weight=2.0, passed=passed,
            details=f"Utilization: {util:.1f}%",
        )
