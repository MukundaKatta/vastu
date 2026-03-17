"""Tests for Vastu data models."""

import pytest
from vastu.models import (
    Direction,
    FloorPlan,
    Remedy,
    Room,
    RoomType,
    VastuRule,
    VastuScore,
)


class TestRoom:
    def test_room_creation(self):
        room = Room(
            name="Master Bedroom", room_type=RoomType.MASTER_BEDROOM,
            x=0, y=0, width=14, length=14, direction=Direction.SOUTHWEST,
        )
        assert room.name == "Master Bedroom"
        assert room.area == 196

    def test_room_area(self):
        room = Room(
            name="Kitchen", room_type=RoomType.KITCHEN,
            x=10, y=5, width=10, length=8, direction=Direction.SOUTHEAST,
        )
        assert room.area == 80

    def test_room_center(self):
        room = Room(
            name="Test", room_type=RoomType.LIVING,
            x=10, y=20, width=16, length=12, direction=Direction.NORTH,
        )
        assert room.center_x == 18
        assert room.center_y == 26


class TestFloorPlan:
    def test_empty_plan(self):
        plan = FloorPlan(width=40, length=50)
        assert plan.total_area == 2000
        assert plan.used_area == 0
        assert plan.utilization == 0

    def test_plan_with_rooms(self):
        rooms = [
            Room(name="R1", room_type=RoomType.LIVING, x=0, y=0, width=10, length=10, direction=Direction.NORTH),
            Room(name="R2", room_type=RoomType.KITCHEN, x=10, y=0, width=8, length=8, direction=Direction.SOUTHEAST),
        ]
        plan = FloorPlan(width=40, length=50, rooms=rooms)
        assert plan.used_area == 164
        assert plan.utilization == pytest.approx(8.2, rel=0.1)

    def test_get_rooms_by_type(self):
        rooms = [
            Room(name="BR1", room_type=RoomType.BEDROOM, x=0, y=0, width=10, length=10, direction=Direction.SOUTH),
            Room(name="BR2", room_type=RoomType.BEDROOM, x=10, y=0, width=10, length=10, direction=Direction.WEST),
            Room(name="K", room_type=RoomType.KITCHEN, x=20, y=0, width=8, length=8, direction=Direction.SOUTHEAST),
        ]
        plan = FloorPlan(width=40, length=50, rooms=rooms)
        assert len(plan.get_rooms_by_type(RoomType.BEDROOM)) == 2
        assert len(plan.get_rooms_by_type(RoomType.KITCHEN)) == 1


class TestVastuScore:
    def test_grade_excellent(self):
        score = VastuScore(overall_score=95, direction_score=90, placement_score=95, proportion_score=100)
        assert score.compute_grade() == "Excellent"

    def test_grade_poor(self):
        score = VastuScore(overall_score=30, direction_score=20, placement_score=40, proportion_score=30)
        assert score.compute_grade() == "Poor"

    def test_grade_good(self):
        score = VastuScore(overall_score=80, direction_score=75, placement_score=85, proportion_score=80)
        assert score.compute_grade() == "Good"


class TestDirection:
    def test_all_directions(self):
        assert len(Direction) == 9

    def test_direction_values(self):
        assert Direction.NORTHEAST.value == "northeast"
        assert Direction.SOUTHWEST.value == "southwest"
