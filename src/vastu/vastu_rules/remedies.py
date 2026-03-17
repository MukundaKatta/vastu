"""Vastu remedy advisor suggesting corrections for non-compliant designs.

When a floor plan fails Vastu rules, the remedy advisor provides:
1. The recommended structural correction (move/relocate)
2. An alternative symbolic/traditional remedy when structural changes are impractical
"""

from __future__ import annotations

from vastu.models import FloorPlan, Remedy, VastuScore


# Remedy database keyed by rule ID
_REMEDY_DATABASE: dict[str, dict] = {
    "V01": {
        "recommended_action": "Relocate kitchen to the Southeast corner of the house.",
        "alternative_remedy": "Place a red or orange light in the Southeast corner. Keep a Vastu pyramid in the kitchen. Ensure the cook faces East while cooking.",
        "severity": "high",
        "priority": 1,
    },
    "V02": {
        "recommended_action": "Move master bedroom to the Southwest zone.",
        "alternative_remedy": "Sleep with head towards South. Place heavy furniture in Southwest corner of the current bedroom. Use earthy colors (brown, beige) in bedroom decor.",
        "severity": "high",
        "priority": 2,
    },
    "V03": {
        "recommended_action": "Create or move puja room/altar to the Northeast corner.",
        "alternative_remedy": "Set up a small prayer shelf in the Northeast corner of any room. Keep the Northeast area clean and clutter-free. Place a water element (fountain or bowl) in NE.",
        "severity": "medium",
        "priority": 4,
    },
    "V04": {
        "recommended_action": "If possible, create the main entrance on the North or East wall.",
        "alternative_remedy": "Place a Vastu Dwar (auspicious door frame) decoration. Use bright lighting at the entrance. Place auspicious symbols (Om, Swastik) above the door. Keep entrance well-lit and clean.",
        "severity": "critical",
        "priority": 1,
    },
    "V05": {
        "recommended_action": "Position the living room in the North or East zone of the house.",
        "alternative_remedy": "Use light colors in the living room. Ensure maximum natural light from North/East windows. Place a mirror on the North wall to enhance Kubera energy.",
        "severity": "medium",
        "priority": 5,
    },
    "V06": {
        "recommended_action": "Move bathrooms to the Northwest or West zone.",
        "alternative_remedy": "Keep bathroom doors closed at all times. Use exhaust fans for ventilation. Place air-purifying plants near bathroom. Use light blue or white colors inside.",
        "severity": "medium",
        "priority": 5,
    },
    "V07": {
        "recommended_action": "Immediately relocate any bathroom/toilet from the Northeast zone.",
        "alternative_remedy": "This is a critical defect. Keep the NE bathroom door permanently closed when not in use. Place a Vastu pyramid inside. Burn camphor regularly. Consider converting to a store or puja if structural change is possible.",
        "severity": "critical",
        "priority": 1,
    },
    "V08": {
        "recommended_action": "Move kitchen out of the Northeast zone to Southeast.",
        "alternative_remedy": "Place a Vastu crystal in the kitchen. Ensure cooking faces East. Keep Northeast corner of kitchen clean and used for water storage.",
        "severity": "high",
        "priority": 2,
    },
    "V09": {
        "recommended_action": "Keep the center (Brahmasthan) of the house open as a courtyard or hall.",
        "alternative_remedy": "If structural change is not possible, keep the center area well-lit with a chandelier or skylight. Place a crystal chandelier at the center. Avoid placing heavy objects in the center.",
        "severity": "high",
        "priority": 3,
    },
    "V10": {
        "recommended_action": "Relocate staircase to the South, West, or Southwest portion.",
        "alternative_remedy": "If staircase cannot be moved, ensure it climbs clockwise. Place a Vastu pyramid under the staircase. Use bright lighting in the staircase area.",
        "severity": "medium",
        "priority": 4,
    },
    "V11": {
        "recommended_action": "Move bedrooms out of the Southeast fire zone.",
        "alternative_remedy": "If bedroom must stay in SE, sleep with head pointing South. Avoid red colors. Use cooling colors (green, blue). Place indoor plants for calming energy.",
        "severity": "medium",
        "priority": 5,
    },
    "V12": {
        "recommended_action": "If constructing new, aim for a square or near-square plot (1:1 to 1:1.5).",
        "alternative_remedy": "Use landscaping to visually balance irregular proportions. Plant trees to create visual boundaries. Build compound walls to regularize the shape.",
        "severity": "low",
        "priority": 8,
    },
    "V13": {
        "recommended_action": "Remove heavy structures from the Northeast and keep it light, open, and clean.",
        "alternative_remedy": "Place water elements (aquarium, fountain) in NE. Use light colors. Ensure maximum windows/openings in Northeast walls. Keep NE floor level lowest.",
        "severity": "high",
        "priority": 3,
    },
    "V14": {
        "recommended_action": "Place heavy furniture, master bedroom, or storage in the Southwest zone.",
        "alternative_remedy": "Use heavy, dark-colored furniture in the SW. Avoid windows in SW wall if possible. Keep SW area elevated (even slightly raised flooring).",
        "severity": "medium",
        "priority": 5,
    },
    "V15": {
        "recommended_action": "Ensure physical separation between bathroom and kitchen with at least one room or corridor in between.",
        "alternative_remedy": "Keep a wall separation. Place salt in a bowl between kitchen and bathroom. Use separate plumbing lines. Keep bathroom door always closed on kitchen side.",
        "severity": "high",
        "priority": 3,
    },
    "V16": {
        "recommended_action": "Place dining room adjacent to or very near the kitchen.",
        "alternative_remedy": "If dining is far from kitchen, create a serving counter or pass-through. Use warm lighting in dining area.",
        "severity": "low",
        "priority": 8,
    },
    "V17": {
        "recommended_action": "Move study room to the West, Southwest, or North zone.",
        "alternative_remedy": "Face North or East while studying/working. Place a globe or books in the North. Use green or yellow colors in the study for concentration.",
        "severity": "low",
        "priority": 7,
    },
    "V18": {
        "recommended_action": "Place store room in Northwest or Southwest.",
        "alternative_remedy": "Keep storage areas clean and organized. Avoid storing broken items. Use NW for frequently used items and SW for heavy/long-term storage.",
        "severity": "low",
        "priority": 8,
    },
    "V19": {
        "recommended_action": "Avoid placing any bedroom in the exact center of the house.",
        "alternative_remedy": "Keep center well-lit. Place a small indoor plant or crystal at the center point. Ensure good air circulation through center.",
        "severity": "medium",
        "priority": 5,
    },
    "V20": {
        "recommended_action": "Avoid South or Southwest main entrance. Prefer North, East, or Northeast.",
        "alternative_remedy": "For existing South entrance: paint the door in bright green. Place auspicious rangoli. Hang a toran (door garland). Use bright lighting. Place Ganesha idol at entrance.",
        "severity": "critical",
        "priority": 1,
    },
    "V21": {
        "recommended_action": "Arrange kitchen so cooking platform is on East wall, allowing cook to face East.",
        "alternative_remedy": "Place a mirror on the East wall of the kitchen so cook can see East. Use East-facing gas burner placement.",
        "severity": "low",
        "priority": 7,
    },
    "V22": {
        "recommended_action": "Redesign elongated rooms to be closer to square proportions (1:1 to 1:1.6).",
        "alternative_remedy": "Use furniture placement to visually break long rooms into zones. Place mirrors on shorter walls. Use rugs/carpets to define square sub-areas.",
        "severity": "low",
        "priority": 9,
    },
    "V23": {
        "recommended_action": "Increase room sizes to meet minimum area requirements for comfort and energy flow.",
        "alternative_remedy": "Use mirrors to visually expand small rooms. Keep rooms clutter-free. Use light colors to create sense of space.",
        "severity": "medium",
        "priority": 6,
    },
    "V24": {
        "recommended_action": "Adjust room sizes so total utilization is between 60-85% of plot area.",
        "alternative_remedy": "If over-utilized, remove non-essential rooms or reduce sizes. If under-utilized, add balconies, verandahs, or open courtyards.",
        "severity": "low",
        "priority": 9,
    },
}


class VastuRemedyAdvisor:
    """Suggests remedies for Vastu non-compliance issues."""

    def get_remedies(self, plan: FloorPlan, score: VastuScore) -> list[Remedy]:
        """Generate remedies for all failed Vastu rules.

        Args:
            plan: The floor plan being evaluated.
            score: The VastuScore with checked rules.

        Returns:
            List of Remedy objects sorted by priority (most critical first).
        """
        remedies: list[Remedy] = []

        for rule in score.rules_checked:
            if rule.passed:
                continue

            remedy_data = _REMEDY_DATABASE.get(rule.id)
            if remedy_data is None:
                continue

            remedies.append(Remedy(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=remedy_data["severity"],
                current_state=rule.details,
                recommended_action=remedy_data["recommended_action"],
                alternative_remedy=remedy_data["alternative_remedy"],
                priority=remedy_data["priority"],
            ))

        remedies.sort(key=lambda r: r.priority)
        return remedies

    def get_critical_remedies(self, plan: FloorPlan, score: VastuScore) -> list[Remedy]:
        """Get only critical and high severity remedies."""
        all_remedies = self.get_remedies(plan, score)
        return [r for r in all_remedies if r.severity in ("critical", "high")]

    def get_summary(self, remedies: list[Remedy]) -> dict[str, int]:
        """Get a count of remedies by severity."""
        summary: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for r in remedies:
            summary[r.severity] = summary.get(r.severity, 0) + 1
        return summary
