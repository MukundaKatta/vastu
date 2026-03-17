"""Pydantic models for Vastu floor plan generation."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Direction(str, Enum):
    """Cardinal and intercardinal directions used in Vastu Shastra."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"
    CENTER = "center"


class RoomType(str, Enum):
    """Types of rooms in a floor plan."""

    MASTER_BEDROOM = "master_bedroom"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    LIVING = "living"
    PUJA = "puja"
    DINING = "dining"
    STUDY = "study"
    STAIRCASE = "staircase"
    STORE = "store"
    ENTRANCE = "entrance"
    BALCONY = "balcony"
    GARAGE = "garage"
    UTILITY = "utility"


class Room(BaseModel):
    """Represents a room in the floor plan."""

    name: str
    room_type: RoomType
    x: float = Field(ge=0, description="X position from west edge in feet")
    y: float = Field(ge=0, description="Y position from south edge in feet")
    width: float = Field(gt=0, description="Room width (east-west) in feet")
    length: float = Field(gt=0, description="Room length (north-south) in feet")
    direction: Direction = Field(description="Vastu direction zone the room occupies")

    @property
    def area(self) -> float:
        """Room area in square feet."""
        return self.width * self.length

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.length / 2


class VastuRule(BaseModel):
    """A single Vastu Shastra rule."""

    id: str
    name: str
    description: str
    category: str
    weight: float = Field(default=1.0, ge=0, le=5.0, description="Importance weight 0-5")
    passed: Optional[bool] = None
    details: str = ""


class VastuScore(BaseModel):
    """Vastu compliance score for a floor plan."""

    overall_score: float = Field(ge=0, le=100, description="Overall Vastu score 0-100")
    direction_score: float = Field(ge=0, le=100)
    placement_score: float = Field(ge=0, le=100)
    proportion_score: float = Field(ge=0, le=100)
    rules_checked: list[VastuRule] = Field(default_factory=list)
    passed_rules: int = 0
    failed_rules: int = 0
    total_rules: int = 0
    grade: str = ""

    def compute_grade(self) -> str:
        if self.overall_score >= 90:
            return "Excellent"
        elif self.overall_score >= 75:
            return "Good"
        elif self.overall_score >= 60:
            return "Acceptable"
        elif self.overall_score >= 40:
            return "Needs Improvement"
        else:
            return "Poor"


class Remedy(BaseModel):
    """A Vastu remedy suggestion."""

    rule_id: str
    rule_name: str
    severity: str = Field(description="low, medium, high, critical")
    current_state: str
    recommended_action: str
    alternative_remedy: str = ""
    priority: int = Field(ge=1, le=10)


class FloorPlan(BaseModel):
    """Complete floor plan with rooms and metadata."""

    width: float = Field(gt=0, description="Plot width (east-west) in feet")
    length: float = Field(gt=0, description="Plot length (north-south) in feet")
    rooms: list[Room] = Field(default_factory=list)
    entrance_direction: Direction = Direction.NORTH
    config: str = Field(default="2bhk", description="Room configuration like 2bhk, 3bhk")
    vastu_score: Optional[VastuScore] = None
    remedies: list[Remedy] = Field(default_factory=list)

    @property
    def total_area(self) -> float:
        return self.width * self.length

    @property
    def used_area(self) -> float:
        return sum(r.area for r in self.rooms)

    @property
    def utilization(self) -> float:
        if self.total_area == 0:
            return 0.0
        return (self.used_area / self.total_area) * 100

    def get_rooms_by_type(self, room_type: RoomType) -> list[Room]:
        return [r for r in self.rooms if r.room_type == room_type]

    def get_rooms_in_direction(self, direction: Direction) -> list[Room]:
        return [r for r in self.rooms if r.direction == direction]
