"""Tests for floor plan generator, room placer, and optimizer."""

import pytest
from vastu.generator.floor_plan import FloorPlanGenerator
from vastu.generator.rooms import RoomPlacer, ROOM_CONFIGS
from vastu.generator.optimizer import SpaceOptimizer
from vastu.models import Direction, FloorPlan, RoomType


class TestFloorPlanGenerator:
    def test_generate_2bhk(self):
        gen = FloorPlanGenerator(width=40, length=50)
        plan = gen.generate("2bhk")
        assert len(plan.rooms) > 0
        assert plan.vastu_score is not None
        assert plan.vastu_score.overall_score > 0

    def test_generate_3bhk(self):
        gen = FloorPlanGenerator(width=50, length=60)
        plan = gen.generate("3bhk")
        assert len(plan.rooms) >= 8

    def test_generate_1bhk(self):
        gen = FloorPlanGenerator(width=30, length=35)
        plan = gen.generate("1bhk")
        assert len(plan.rooms) >= 3

    def test_invalid_dimensions(self):
        with pytest.raises(ValueError):
            FloorPlanGenerator(width=-10, length=50)

    def test_too_small_dimensions(self):
        with pytest.raises(ValueError):
            FloorPlanGenerator(width=10, length=10)

    def test_generate_with_entrance(self):
        gen = FloorPlanGenerator(width=40, length=50, entrance=Direction.EAST)
        plan = gen.generate("2bhk")
        assert plan.entrance_direction == Direction.EAST

    def test_generate_multiple(self):
        gen = FloorPlanGenerator(width=40, length=50)
        plans = gen.generate_multiple("2bhk", count=3)
        assert len(plans) >= 1
        # Should be sorted by score (descending)
        scores = [p.vastu_score.overall_score for p in plans]
        assert scores == sorted(scores, reverse=True)

    def test_no_optimize_flag(self):
        gen = FloorPlanGenerator(width=40, length=50, optimize=False)
        plan = gen.generate("2bhk")
        assert plan.vastu_score is not None


class TestRoomPlacer:
    def test_place_2bhk_rooms(self):
        placer = RoomPlacer(40, 50)
        rooms = placer.place_rooms("2bhk")
        assert len(rooms) > 0
        room_types = {r.room_type for r in rooms}
        assert RoomType.MASTER_BEDROOM in room_types
        assert RoomType.KITCHEN in room_types

    def test_invalid_config(self):
        placer = RoomPlacer(40, 50)
        with pytest.raises(ValueError):
            placer.place_rooms("10bhk")

    def test_all_configs_exist(self):
        assert "1bhk" in ROOM_CONFIGS
        assert "2bhk" in ROOM_CONFIGS
        assert "3bhk" in ROOM_CONFIGS
        assert "4bhk" in ROOM_CONFIGS

    def test_no_room_overlap(self):
        placer = RoomPlacer(50, 60)
        rooms = placer.place_rooms("3bhk")
        for i, r1 in enumerate(rooms):
            for j, r2 in enumerate(rooms):
                if i >= j:
                    continue
                overlap = (
                    r1.x < r2.x + r2.width and r1.x + r1.width > r2.x and
                    r1.y < r2.y + r2.length and r1.y + r1.length > r2.y
                )
                assert not overlap, f"{r1.name} overlaps {r2.name}"


class TestSpaceOptimizer:
    def test_optimization_improves_or_maintains(self):
        placer = RoomPlacer(40, 50)
        rooms = placer.place_rooms("2bhk")
        plan = FloorPlan(width=40, length=50, rooms=rooms, entrance_direction=Direction.NORTH, config="2bhk")

        original_area = plan.used_area

        optimizer = SpaceOptimizer(max_iterations=10)
        optimized = optimizer.optimize(plan)

        assert optimized.used_area >= original_area

    def test_utilization_report(self):
        gen = FloorPlanGenerator(width=40, length=50, optimize=False)
        plan = gen.generate("2bhk")
        optimizer = SpaceOptimizer()
        report = optimizer.get_utilization_report(plan)

        assert "total_plot_area_sqft" in report
        assert "used_area_sqft" in report
        assert "utilization_pct" in report
        assert report["total_plot_area_sqft"] == 2000
