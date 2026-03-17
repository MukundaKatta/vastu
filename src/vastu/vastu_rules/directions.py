"""Directional rules based on Vastu Shastra principles.

Vastu Shastra associates each direction with specific elements, deities,
and purposes. This module encodes those traditional associations into
programmatic rules for room placement validation.
"""

from __future__ import annotations

from vastu.models import Direction, RoomType


# Vastu directional deity/element associations
DIRECTION_ELEMENTS = {
    Direction.NORTH: {"deity": "Kubera", "element": "Water", "governs": "wealth, career"},
    Direction.SOUTH: {"deity": "Yama", "element": "Earth", "governs": "fame, dharma"},
    Direction.EAST: {"deity": "Indra", "element": "Fire (Sun)", "governs": "health, social"},
    Direction.WEST: {"deity": "Varuna", "element": "Water", "governs": "luck, gains"},
    Direction.NORTHEAST: {"deity": "Ishanya (Shiva)", "element": "Water", "governs": "spirituality, wisdom"},
    Direction.NORTHWEST: {"deity": "Vayu", "element": "Air", "governs": "movement, change"},
    Direction.SOUTHEAST: {"deity": "Agni", "element": "Fire", "governs": "energy, cooking"},
    Direction.SOUTHWEST: {"deity": "Nairuti", "element": "Earth", "governs": "stability, strength"},
    Direction.CENTER: {"deity": "Brahma", "element": "Space (Akasha)", "governs": "Brahmasthan, open space"},
}


class DirectionalRules:
    """Encodes Vastu Shastra directional placement principles.

    Core Vastu directional rules:
    1. Kitchen in Southeast (Agni/fire corner) - fire element alignment
    2. Master bedroom in Southwest (Nairuti) - stability and grounding
    3. Puja/prayer room in Northeast (Ishanya) - spiritual purity
    4. Entrance facing North or East - invites prosperity and sunlight
    5. Living room in North or Northeast - wealth and openness
    6. Bathrooms in Northwest or West - Vayu aids ventilation
    7. Dining room in West or adjacent to kitchen
    8. Study/office in West or Southwest - concentration
    9. Staircase in South, West, or Southwest - never Northeast
    10. Store room in Northwest or Southwest
    11. Garage in Northwest or Southeast
    12. Balcony in North or East - morning sunlight
    13. Utility room in Northwest
    14. Guest bedroom in Northwest - transient nature (Vayu)
    """

    # Ideal directions for each room type (ordered by preference)
    IDEAL_PLACEMENTS: dict[RoomType, list[Direction]] = {
        RoomType.KITCHEN: [Direction.SOUTHEAST, Direction.SOUTH, Direction.EAST],
        RoomType.MASTER_BEDROOM: [Direction.SOUTHWEST, Direction.SOUTH, Direction.WEST],
        RoomType.BEDROOM: [Direction.SOUTH, Direction.WEST, Direction.SOUTHWEST, Direction.NORTHWEST],
        RoomType.PUJA: [Direction.NORTHEAST, Direction.NORTH, Direction.EAST],
        RoomType.ENTRANCE: [Direction.NORTH, Direction.EAST, Direction.NORTHEAST],
        RoomType.LIVING: [Direction.NORTH, Direction.EAST, Direction.NORTHEAST],
        RoomType.BATHROOM: [Direction.NORTHWEST, Direction.WEST],
        RoomType.DINING: [Direction.WEST, Direction.EAST, Direction.SOUTH],
        RoomType.STUDY: [Direction.WEST, Direction.SOUTHWEST, Direction.NORTH],
        RoomType.STAIRCASE: [Direction.SOUTH, Direction.WEST, Direction.SOUTHWEST],
        RoomType.STORE: [Direction.NORTHWEST, Direction.SOUTHWEST],
        RoomType.BALCONY: [Direction.NORTH, Direction.EAST, Direction.NORTHEAST],
        RoomType.GARAGE: [Direction.NORTHWEST, Direction.SOUTHEAST],
        RoomType.UTILITY: [Direction.NORTHWEST, Direction.WEST],
    }

    # Directions that are strictly prohibited for each room type
    PROHIBITED_PLACEMENTS: dict[RoomType, list[Direction]] = {
        RoomType.KITCHEN: [Direction.NORTHEAST, Direction.NORTH],
        RoomType.MASTER_BEDROOM: [Direction.NORTHEAST, Direction.SOUTHEAST],
        RoomType.PUJA: [Direction.SOUTH, Direction.SOUTHWEST, Direction.SOUTHEAST],
        RoomType.ENTRANCE: [Direction.SOUTH, Direction.SOUTHWEST],
        RoomType.BATHROOM: [Direction.NORTHEAST, Direction.SOUTHEAST, Direction.CENTER],
        RoomType.STAIRCASE: [Direction.NORTHEAST, Direction.CENTER],
        RoomType.LIVING: [Direction.SOUTHWEST, Direction.SOUTH],
    }

    @classmethod
    def get_ideal_directions(cls, room_type: RoomType) -> list[Direction]:
        """Get ideal Vastu directions for a room type."""
        return cls.IDEAL_PLACEMENTS.get(room_type, [])

    @classmethod
    def get_prohibited_directions(cls, room_type: RoomType) -> list[Direction]:
        """Get prohibited Vastu directions for a room type."""
        return cls.PROHIBITED_PLACEMENTS.get(room_type, [])

    @classmethod
    def is_ideal_placement(cls, room_type: RoomType, direction: Direction) -> bool:
        """Check if a room is in its ideal Vastu direction."""
        ideal = cls.IDEAL_PLACEMENTS.get(room_type, [])
        return direction in ideal

    @classmethod
    def is_prohibited_placement(cls, room_type: RoomType, direction: Direction) -> bool:
        """Check if a room is in a prohibited Vastu direction."""
        prohibited = cls.PROHIBITED_PLACEMENTS.get(room_type, [])
        return direction in prohibited

    @classmethod
    def get_placement_score(cls, room_type: RoomType, direction: Direction) -> float:
        """Score a room placement from 0 (prohibited) to 1 (ideal).

        Returns:
            1.0 if first-choice ideal direction
            0.8 if second-choice ideal direction
            0.6 if third-choice ideal direction
            0.4 if neutral (neither ideal nor prohibited)
            0.0 if prohibited
        """
        if cls.is_prohibited_placement(room_type, direction):
            return 0.0
        ideal = cls.IDEAL_PLACEMENTS.get(room_type, [])
        if direction in ideal:
            idx = ideal.index(direction)
            return max(0.6, 1.0 - idx * 0.2)
        return 0.4

    @classmethod
    def determine_direction(
        cls, x: float, y: float, width: float, length: float,
        plot_width: float, plot_length: float,
    ) -> Direction:
        """Determine which Vastu direction zone a point falls in.

        The plot is divided into a 3x3 grid:
            NW | N  | NE
            W  | C  | E
            SW | S  | SE

        Args:
            x, y: Position of the room's center.
            width, length: Not used for center-based calculation but kept for API.
            plot_width: Total plot width (east-west).
            plot_length: Total plot length (north-south).
        """
        third_w = plot_width / 3
        third_l = plot_length / 3

        if x < third_w:
            col = "west"
        elif x < 2 * third_w:
            col = "center"
        else:
            col = "east"

        if y < third_l:
            row = "south"
        elif y < 2 * third_l:
            row = "center"
        else:
            row = "north"

        direction_map = {
            ("south", "west"): Direction.SOUTHWEST,
            ("south", "center"): Direction.SOUTH,
            ("south", "east"): Direction.SOUTHEAST,
            ("center", "west"): Direction.WEST,
            ("center", "center"): Direction.CENTER,
            ("center", "east"): Direction.EAST,
            ("north", "west"): Direction.NORTHWEST,
            ("north", "center"): Direction.NORTH,
            ("north", "east"): Direction.NORTHEAST,
        }
        return direction_map.get((row, col), Direction.CENTER)

    @classmethod
    def get_direction_info(cls, direction: Direction) -> dict:
        """Get Vastu information about a direction."""
        return DIRECTION_ELEMENTS.get(direction, {})
