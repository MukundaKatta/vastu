"""Tests for Vastu compliance checker."""

import pytest
from vastu.models import Direction, FloorPlan, Room, RoomType
from vastu.vastu_rules.compliance import VastuComplianceChecker


@pytest.fixture
def checker():
    return VastuComplianceChecker()


@pytest.fixture
def good_plan():
    """A plan with rooms placed in ideal Vastu positions."""
    return FloorPlan(
        width=45, length=50,
        entrance_direction=Direction.NORTH,
        config="2bhk",
        rooms=[
            Room(name="Master Bedroom", room_type=RoomType.MASTER_BEDROOM,
                 x=0, y=0, width=14, length=14, direction=Direction.SOUTHWEST),
            Room(name="Bedroom 2", room_type=RoomType.BEDROOM,
                 x=0, y=33, width=12, length=12, direction=Direction.NORTHWEST),
            Room(name="Living Room", room_type=RoomType.LIVING,
                 x=15, y=33, width=16, length=14, direction=Direction.NORTH),
            Room(name="Kitchen", room_type=RoomType.KITCHEN,
                 x=31, y=0, width=10, length=10, direction=Direction.SOUTHEAST),
            Room(name="Bathroom 1", room_type=RoomType.BATHROOM,
                 x=0, y=14, width=7, length=8, direction=Direction.WEST),
            Room(name="Bathroom 2", room_type=RoomType.BATHROOM,
                 x=0, y=22, width=6, length=7, direction=Direction.WEST),
            Room(name="Puja", room_type=RoomType.PUJA,
                 x=35, y=40, width=5, length=5, direction=Direction.NORTHEAST),
        ],
    )


@pytest.fixture
def bad_plan():
    """A plan with multiple Vastu violations."""
    return FloorPlan(
        width=40, length=40,
        entrance_direction=Direction.SOUTH,
        config="2bhk",
        rooms=[
            Room(name="Master Bedroom", room_type=RoomType.MASTER_BEDROOM,
                 x=28, y=28, width=12, length=12, direction=Direction.NORTHEAST),
            Room(name="Kitchen", room_type=RoomType.KITCHEN,
                 x=28, y=0, width=10, length=10, direction=Direction.NORTHEAST),
            Room(name="Bathroom", room_type=RoomType.BATHROOM,
                 x=30, y=30, width=6, length=6, direction=Direction.NORTHEAST),
            Room(name="Living", room_type=RoomType.LIVING,
                 x=0, y=0, width=14, length=14, direction=Direction.SOUTHWEST),
        ],
    )


class TestVastuComplianceChecker:
    def test_good_plan_scores_well(self, checker, good_plan):
        score = checker.check_compliance(good_plan)
        assert score.overall_score >= 50
        assert score.total_rules >= 20
        assert score.grade in ("Excellent", "Good", "Acceptable")

    def test_bad_plan_scores_poorly(self, checker, bad_plan):
        score = checker.check_compliance(bad_plan)
        assert score.overall_score < 60
        assert score.failed_rules > 5

    def test_minimum_24_rules(self, checker, good_plan):
        score = checker.check_compliance(good_plan)
        assert score.total_rules >= 24

    def test_kitchen_southeast_passes(self, checker, good_plan):
        score = checker.check_compliance(good_plan)
        kitchen_rule = next(r for r in score.rules_checked if r.id == "V01")
        assert kitchen_rule.passed is True

    def test_entrance_south_fails(self, checker, bad_plan):
        score = checker.check_compliance(bad_plan)
        entrance_rule = next(r for r in score.rules_checked if r.id == "V04")
        assert entrance_rule.passed is False

    def test_bathroom_northeast_fails(self, checker, bad_plan):
        score = checker.check_compliance(bad_plan)
        rule = next(r for r in score.rules_checked if r.id == "V07")
        assert rule.passed is False

    def test_score_has_categories(self, checker, good_plan):
        score = checker.check_compliance(good_plan)
        assert 0 <= score.direction_score <= 100
        assert 0 <= score.placement_score <= 100
        assert 0 <= score.proportion_score <= 100
