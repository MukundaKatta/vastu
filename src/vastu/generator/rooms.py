"""Room placement engine following Vastu directional guidelines.

Places rooms in their ideal Vastu zones while respecting size constraints
and avoiding overlaps.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from vastu.models import Direction, FloorPlan, Room, RoomType
from vastu.vastu_rules.directions import DirectionalRules


# Default room configurations
ROOM_CONFIGS: dict[str, list[dict]] = {
    "1bhk": [
        {"name": "Master Bedroom", "type": RoomType.MASTER_BEDROOM, "min_w": 12, "min_l": 12},
        {"name": "Living Room", "type": RoomType.LIVING, "min_w": 12, "min_l": 14},
        {"name": "Kitchen", "type": RoomType.KITCHEN, "min_w": 8, "min_l": 8},
        {"name": "Bathroom 1", "type": RoomType.BATHROOM, "min_w": 6, "min_l": 7},
        {"name": "Entrance", "type": RoomType.ENTRANCE, "min_w": 5, "min_l": 5},
    ],
    "2bhk": [
        {"name": "Master Bedroom", "type": RoomType.MASTER_BEDROOM, "min_w": 12, "min_l": 14},
        {"name": "Bedroom 2", "type": RoomType.BEDROOM, "min_w": 10, "min_l": 12},
        {"name": "Living Room", "type": RoomType.LIVING, "min_w": 14, "min_l": 12},
        {"name": "Kitchen", "type": RoomType.KITCHEN, "min_w": 8, "min_l": 10},
        {"name": "Bathroom 1", "type": RoomType.BATHROOM, "min_w": 6, "min_l": 7},
        {"name": "Bathroom 2", "type": RoomType.BATHROOM, "min_w": 5, "min_l": 6},
        {"name": "Puja Room", "type": RoomType.PUJA, "min_w": 5, "min_l": 5},
        {"name": "Entrance", "type": RoomType.ENTRANCE, "min_w": 5, "min_l": 5},
    ],
    "3bhk": [
        {"name": "Master Bedroom", "type": RoomType.MASTER_BEDROOM, "min_w": 14, "min_l": 14},
        {"name": "Bedroom 2", "type": RoomType.BEDROOM, "min_w": 12, "min_l": 12},
        {"name": "Bedroom 3", "type": RoomType.BEDROOM, "min_w": 10, "min_l": 12},
        {"name": "Living Room", "type": RoomType.LIVING, "min_w": 16, "min_l": 14},
        {"name": "Kitchen", "type": RoomType.KITCHEN, "min_w": 10, "min_l": 10},
        {"name": "Dining Room", "type": RoomType.DINING, "min_w": 10, "min_l": 10},
        {"name": "Bathroom 1", "type": RoomType.BATHROOM, "min_w": 6, "min_l": 8},
        {"name": "Bathroom 2", "type": RoomType.BATHROOM, "min_w": 5, "min_l": 7},
        {"name": "Bathroom 3", "type": RoomType.BATHROOM, "min_w": 5, "min_l": 6},
        {"name": "Puja Room", "type": RoomType.PUJA, "min_w": 5, "min_l": 5},
        {"name": "Entrance", "type": RoomType.ENTRANCE, "min_w": 5, "min_l": 5},
    ],
    "4bhk": [
        {"name": "Master Bedroom", "type": RoomType.MASTER_BEDROOM, "min_w": 14, "min_l": 16},
        {"name": "Bedroom 2", "type": RoomType.BEDROOM, "min_w": 12, "min_l": 14},
        {"name": "Bedroom 3", "type": RoomType.BEDROOM, "min_w": 12, "min_l": 12},
        {"name": "Bedroom 4", "type": RoomType.BEDROOM, "min_w": 10, "min_l": 12},
        {"name": "Living Room", "type": RoomType.LIVING, "min_w": 18, "min_l": 16},
        {"name": "Kitchen", "type": RoomType.KITCHEN, "min_w": 10, "min_l": 12},
        {"name": "Dining Room", "type": RoomType.DINING, "min_w": 12, "min_l": 10},
        {"name": "Study Room", "type": RoomType.STUDY, "min_w": 8, "min_l": 10},
        {"name": "Bathroom 1", "type": RoomType.BATHROOM, "min_w": 6, "min_l": 8},
        {"name": "Bathroom 2", "type": RoomType.BATHROOM, "min_w": 6, "min_l": 7},
        {"name": "Bathroom 3", "type": RoomType.BATHROOM, "min_w": 5, "min_l": 7},
        {"name": "Bathroom 4", "type": RoomType.BATHROOM, "min_w": 5, "min_l": 6},
        {"name": "Puja Room", "type": RoomType.PUJA, "min_w": 6, "min_l": 6},
        {"name": "Entrance", "type": RoomType.ENTRANCE, "min_w": 6, "min_l": 6},
    ],
}


class RoomPlacer:
    """Places rooms in a floor plan according to Vastu directional rules.

    The placer divides the plot into a 3x3 Vastu grid and assigns rooms
    to their ideal directional zones, then positions them to avoid overlap.
    """

    def __init__(self, plot_width: float, plot_length: float):
        self.plot_width = plot_width
        self.plot_length = plot_length
        self._grid = np.zeros((int(plot_length), int(plot_width)), dtype=int)
        self._placed_rooms: list[Room] = []

    def get_room_config(self, config: str) -> list[dict]:
        """Get room specifications for a given configuration."""
        config = config.lower().strip()
        if config not in ROOM_CONFIGS:
            raise ValueError(f"Unknown config '{config}'. Available: {list(ROOM_CONFIGS.keys())}")
        return ROOM_CONFIGS[config]

    def place_rooms(self, config: str) -> list[Room]:
        """Place all rooms for a given configuration.

        Strategy:
        1. Sort rooms by Vastu priority (most constrained first).
        2. For each room, find the ideal zone and place it there.
        3. Fall back to secondary zones if ideal is occupied.
        """
        room_specs = self.get_room_config(config)
        self._placed_rooms = []

        # Priority order: rooms with most specific Vastu requirements first
        priority_order = [
            RoomType.KITCHEN,        # Must be SE
            RoomType.MASTER_BEDROOM, # Must be SW
            RoomType.PUJA,           # Must be NE
            RoomType.ENTRANCE,       # Must be N/E
            RoomType.LIVING,         # N/E preferred
            RoomType.BATHROOM,       # NW/W preferred
            RoomType.BEDROOM,        # S/W/SW
            RoomType.DINING,         # W/E
            RoomType.STUDY,          # W/SW
            RoomType.STAIRCASE,      # S/W/SW
            RoomType.STORE,          # NW/SW
            RoomType.BALCONY,
            RoomType.GARAGE,
            RoomType.UTILITY,
        ]

        sorted_specs = sorted(
            room_specs,
            key=lambda s: priority_order.index(s["type"]) if s["type"] in priority_order else 99,
        )

        for spec in sorted_specs:
            room = self._place_single_room(spec)
            if room:
                self._placed_rooms.append(room)

        return self._placed_rooms

    def _place_single_room(self, spec: dict) -> Optional[Room]:
        """Place a single room in its ideal Vastu zone."""
        room_type: RoomType = spec["type"]
        min_w = spec["min_w"]
        min_l = spec["min_l"]

        ideal_directions = DirectionalRules.get_ideal_directions(room_type)
        if not ideal_directions:
            ideal_directions = [Direction.CENTER]

        for direction in ideal_directions:
            position = self._find_position_in_zone(direction, min_w, min_l)
            if position is not None:
                x, y = position
                actual_dir = DirectionalRules.determine_direction(
                    x + min_w / 2, y + min_l / 2, min_w, min_l,
                    self.plot_width, self.plot_length,
                )
                room = Room(
                    name=spec["name"],
                    room_type=room_type,
                    x=x, y=y,
                    width=min_w, length=min_l,
                    direction=actual_dir,
                )
                self._mark_occupied(x, y, min_w, min_l)
                return room

        # Fallback: try any available position
        for direction in Direction:
            if direction in ideal_directions:
                continue
            position = self._find_position_in_zone(direction, min_w, min_l)
            if position is not None:
                x, y = position
                actual_dir = DirectionalRules.determine_direction(
                    x + min_w / 2, y + min_l / 2, min_w, min_l,
                    self.plot_width, self.plot_length,
                )
                room = Room(
                    name=spec["name"],
                    room_type=room_type,
                    x=x, y=y,
                    width=min_w, length=min_l,
                    direction=actual_dir,
                )
                self._mark_occupied(x, y, min_w, min_l)
                return room

        return None

    def _find_position_in_zone(
        self, direction: Direction, width: float, length: float,
    ) -> Optional[tuple[float, float]]:
        """Find an unoccupied position within a Vastu zone."""
        third_w = self.plot_width / 3
        third_l = self.plot_length / 3

        zone_bounds = {
            Direction.SOUTHWEST: (0, 0, third_w, third_l),
            Direction.SOUTH: (third_w, 0, 2 * third_w, third_l),
            Direction.SOUTHEAST: (2 * third_w, 0, self.plot_width, third_l),
            Direction.WEST: (0, third_l, third_w, 2 * third_l),
            Direction.CENTER: (third_w, third_l, 2 * third_w, 2 * third_l),
            Direction.EAST: (2 * third_w, third_l, self.plot_width, 2 * third_l),
            Direction.NORTHWEST: (0, 2 * third_l, third_w, self.plot_length),
            Direction.NORTH: (third_w, 2 * third_l, 2 * third_w, self.plot_length),
            Direction.NORTHEAST: (2 * third_w, 2 * third_l, self.plot_width, self.plot_length),
        }

        bounds = zone_bounds.get(direction)
        if bounds is None:
            return None

        x_min, y_min, x_max, y_max = bounds
        zone_w = x_max - x_min
        zone_l = y_max - y_min

        if width > zone_w or length > zone_l:
            # Room too big for zone - try fitting with some overflow
            if width > zone_w * 1.5 or length > zone_l * 1.5:
                return None

        # Try placing at zone start, scanning for non-overlap
        step = 1.0
        for x in np.arange(x_min, min(x_max, self.plot_width - width) + 0.1, step):
            for y in np.arange(y_min, min(y_max, self.plot_length - length) + 0.1, step):
                if not self._overlaps(x, y, width, length):
                    return (float(x), float(y))

        return None

    def _overlaps(self, x: float, y: float, w: float, l: float) -> bool:
        """Check if a proposed room rectangle overlaps with existing rooms."""
        for room in self._placed_rooms:
            if (x < room.x + room.width and x + w > room.x and
                    y < room.y + room.length and y + l > room.y):
                return True
        return False

    def _mark_occupied(self, x: float, y: float, w: float, l: float) -> None:
        """Mark grid cells as occupied (for visualization purposes)."""
        x_start = max(0, int(x))
        y_start = max(0, int(y))
        x_end = min(self._grid.shape[1], int(x + w))
        y_end = min(self._grid.shape[0], int(y + l))
        self._grid[y_start:y_end, x_start:x_end] = 1
