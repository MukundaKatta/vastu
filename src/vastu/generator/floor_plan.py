"""Floor plan generator creating room layouts optimized for space and Vastu.

This is the main entry point for generating Vastu-compliant floor plans.
It orchestrates room placement, optimization, compliance checking, and
remedy generation.
"""

from __future__ import annotations

from vastu.models import Direction, FloorPlan, RoomType
from vastu.generator.rooms import RoomPlacer
from vastu.generator.optimizer import SpaceOptimizer
from vastu.vastu_rules.compliance import VastuComplianceChecker
from vastu.vastu_rules.remedies import VastuRemedyAdvisor


class FloorPlanGenerator:
    """Generates Vastu-compliant floor plans for given plot dimensions.

    Usage:
        generator = FloorPlanGenerator(width=40, length=50)
        plan = generator.generate(room_config="3bhk")
        print(f"Score: {plan.vastu_score.overall_score}")
    """

    def __init__(
        self,
        width: float,
        length: float,
        entrance: Direction = Direction.NORTH,
        optimize: bool = True,
        max_optimize_iterations: int = 50,
    ):
        """Initialize the generator.

        Args:
            width: Plot width (east-west) in feet.
            length: Plot length (north-south) in feet.
            entrance: Direction of main entrance.
            optimize: Whether to run space optimization.
            max_optimize_iterations: Max iterations for optimizer.
        """
        if width <= 0 or length <= 0:
            raise ValueError("Plot dimensions must be positive.")
        if width < 20 or length < 20:
            raise ValueError("Plot dimensions must be at least 20 feet.")

        self.width = width
        self.length = length
        self.entrance = entrance
        self.optimize = optimize
        self.max_optimize_iterations = max_optimize_iterations

    def generate(self, room_config: str = "2bhk") -> FloorPlan:
        """Generate a complete Vastu-compliant floor plan.

        Args:
            room_config: Room configuration (1bhk, 2bhk, 3bhk, 4bhk).

        Returns:
            FloorPlan with rooms placed, scored, and remedies attached.
        """
        # Step 1: Place rooms according to Vastu rules
        placer = RoomPlacer(self.width, self.length)
        rooms = placer.place_rooms(room_config)

        plan = FloorPlan(
            width=self.width,
            length=self.length,
            rooms=rooms,
            entrance_direction=self.entrance,
            config=room_config,
        )

        # Step 2: Optimize space utilization
        if self.optimize:
            optimizer = SpaceOptimizer(max_iterations=self.max_optimize_iterations)
            plan = optimizer.optimize(plan)

        # Step 3: Check Vastu compliance
        checker = VastuComplianceChecker()
        plan.vastu_score = checker.check_compliance(plan)

        # Step 4: Generate remedies for failures
        advisor = VastuRemedyAdvisor()
        plan.remedies = advisor.get_remedies(plan, plan.vastu_score)

        return plan

    def generate_multiple(
        self, room_config: str = "2bhk", count: int = 3,
    ) -> list[FloorPlan]:
        """Generate multiple plan variants and return sorted by score.

        Args:
            room_config: Room configuration.
            count: Number of variants to generate.

        Returns:
            List of FloorPlan objects sorted by Vastu score (best first).
        """
        plans = []
        entrances = [Direction.NORTH, Direction.EAST, Direction.NORTHEAST]

        for i in range(min(count, len(entrances))):
            self.entrance = entrances[i]
            plan = self.generate(room_config)
            plans.append(plan)

        plans.sort(
            key=lambda p: p.vastu_score.overall_score if p.vastu_score else 0,
            reverse=True,
        )
        return plans
