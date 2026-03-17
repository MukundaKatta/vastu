"""Tests for Vastu remedy advisor."""

import pytest
from vastu.models import Direction, FloorPlan, Room, RoomType
from vastu.vastu_rules.compliance import VastuComplianceChecker
from vastu.vastu_rules.remedies import VastuRemedyAdvisor


@pytest.fixture
def advisor():
    return VastuRemedyAdvisor()


@pytest.fixture
def checker():
    return VastuComplianceChecker()


@pytest.fixture
def non_compliant_plan():
    return FloorPlan(
        width=40, length=40,
        entrance_direction=Direction.SOUTH,
        config="2bhk",
        rooms=[
            Room(name="Master BR", room_type=RoomType.MASTER_BEDROOM,
                 x=28, y=28, width=12, length=12, direction=Direction.NORTHEAST),
            Room(name="Kitchen", room_type=RoomType.KITCHEN,
                 x=0, y=28, width=10, length=10, direction=Direction.NORTHWEST),
            Room(name="Bathroom", room_type=RoomType.BATHROOM,
                 x=30, y=30, width=6, length=6, direction=Direction.NORTHEAST),
            Room(name="Living", room_type=RoomType.LIVING,
                 x=0, y=0, width=14, length=14, direction=Direction.SOUTHWEST),
        ],
    )


class TestVastuRemedyAdvisor:
    def test_remedies_for_non_compliant(self, advisor, checker, non_compliant_plan):
        score = checker.check_compliance(non_compliant_plan)
        remedies = advisor.get_remedies(non_compliant_plan, score)
        assert len(remedies) > 0

    def test_remedies_sorted_by_priority(self, advisor, checker, non_compliant_plan):
        score = checker.check_compliance(non_compliant_plan)
        remedies = advisor.get_remedies(non_compliant_plan, score)
        priorities = [r.priority for r in remedies]
        assert priorities == sorted(priorities)

    def test_critical_remedies(self, advisor, checker, non_compliant_plan):
        score = checker.check_compliance(non_compliant_plan)
        critical = advisor.get_critical_remedies(non_compliant_plan, score)
        for r in critical:
            assert r.severity in ("critical", "high")

    def test_remedy_has_alternative(self, advisor, checker, non_compliant_plan):
        score = checker.check_compliance(non_compliant_plan)
        remedies = advisor.get_remedies(non_compliant_plan, score)
        for r in remedies:
            assert r.recommended_action != ""

    def test_summary_counts(self, advisor, checker, non_compliant_plan):
        score = checker.check_compliance(non_compliant_plan)
        remedies = advisor.get_remedies(non_compliant_plan, score)
        summary = advisor.get_summary(remedies)
        total = sum(summary.values())
        assert total == len(remedies)

    def test_compliant_plan_fewer_remedies(self, advisor, checker):
        plan = FloorPlan(
            width=45, length=50,
            entrance_direction=Direction.NORTH,
            config="2bhk",
            rooms=[
                Room(name="Master BR", room_type=RoomType.MASTER_BEDROOM,
                     x=0, y=0, width=14, length=14, direction=Direction.SOUTHWEST),
                Room(name="Kitchen", room_type=RoomType.KITCHEN,
                     x=31, y=0, width=10, length=10, direction=Direction.SOUTHEAST),
                Room(name="Living", room_type=RoomType.LIVING,
                     x=15, y=34, width=16, length=14, direction=Direction.NORTH),
                Room(name="Puja", room_type=RoomType.PUJA,
                     x=35, y=40, width=5, length=5, direction=Direction.NORTHEAST),
                Room(name="Bathroom", room_type=RoomType.BATHROOM,
                     x=0, y=33, width=7, length=8, direction=Direction.NORTHWEST),
            ],
        )
        score = checker.check_compliance(plan)
        remedies = advisor.get_remedies(plan, score)
        # Good plan should have fewer remedies
        assert len(remedies) < 15
