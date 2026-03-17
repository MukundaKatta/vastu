"""Tests for Vastu directional rules."""

import pytest
from vastu.models import Direction, RoomType
from vastu.vastu_rules.directions import DirectionalRules


class TestDirectionalRules:
    def test_kitchen_ideal_southeast(self):
        assert DirectionalRules.is_ideal_placement(RoomType.KITCHEN, Direction.SOUTHEAST)

    def test_kitchen_prohibited_northeast(self):
        assert DirectionalRules.is_prohibited_placement(RoomType.KITCHEN, Direction.NORTHEAST)

    def test_master_bedroom_ideal_southwest(self):
        assert DirectionalRules.is_ideal_placement(RoomType.MASTER_BEDROOM, Direction.SOUTHWEST)

    def test_puja_ideal_northeast(self):
        assert DirectionalRules.is_ideal_placement(RoomType.PUJA, Direction.NORTHEAST)

    def test_puja_prohibited_south(self):
        assert DirectionalRules.is_prohibited_placement(RoomType.PUJA, Direction.SOUTH)

    def test_entrance_ideal_north(self):
        assert DirectionalRules.is_ideal_placement(RoomType.ENTRANCE, Direction.NORTH)

    def test_entrance_ideal_east(self):
        assert DirectionalRules.is_ideal_placement(RoomType.ENTRANCE, Direction.EAST)

    def test_bathroom_ideal_northwest(self):
        assert DirectionalRules.is_ideal_placement(RoomType.BATHROOM, Direction.NORTHWEST)

    def test_bathroom_prohibited_northeast(self):
        assert DirectionalRules.is_prohibited_placement(RoomType.BATHROOM, Direction.NORTHEAST)

    def test_placement_score_ideal(self):
        score = DirectionalRules.get_placement_score(RoomType.KITCHEN, Direction.SOUTHEAST)
        assert score == 1.0

    def test_placement_score_prohibited(self):
        score = DirectionalRules.get_placement_score(RoomType.KITCHEN, Direction.NORTHEAST)
        assert score == 0.0

    def test_placement_score_neutral(self):
        score = DirectionalRules.get_placement_score(RoomType.KITCHEN, Direction.NORTHWEST)
        assert score == 0.4

    def test_determine_direction_southwest(self):
        d = DirectionalRules.determine_direction(5, 5, 10, 10, 60, 60)
        assert d == Direction.SOUTHWEST

    def test_determine_direction_northeast(self):
        d = DirectionalRules.determine_direction(50, 50, 10, 10, 60, 60)
        assert d == Direction.NORTHEAST

    def test_determine_direction_center(self):
        d = DirectionalRules.determine_direction(30, 30, 10, 10, 60, 60)
        assert d == Direction.CENTER

    def test_get_direction_info(self):
        info = DirectionalRules.get_direction_info(Direction.SOUTHEAST)
        assert info["deity"] == "Agni"
        assert info["element"] == "Fire"


class TestDirectionElements:
    def test_all_directions_have_info(self):
        from vastu.vastu_rules.directions import DIRECTION_ELEMENTS
        for d in Direction:
            assert d in DIRECTION_ELEMENTS

    def test_northeast_ishanya(self):
        from vastu.vastu_rules.directions import DIRECTION_ELEMENTS
        assert "Ishanya" in DIRECTION_ELEMENTS[Direction.NORTHEAST]["deity"]
