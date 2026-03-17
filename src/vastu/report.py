"""Report generation for Vastu floor plans using Rich tables."""

from __future__ import annotations

import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from vastu.models import FloorPlan, Remedy, VastuScore


class VastuReportGenerator:
    """Generates rich terminal reports for Vastu floor plans."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def print_full_report(self, plan: FloorPlan) -> None:
        """Print a complete Vastu report."""
        self.print_plan_summary(plan)
        self.print_room_layout(plan)
        if plan.vastu_score:
            self.print_vastu_score(plan.vastu_score)
            self.print_rules_detail(plan.vastu_score)
        if plan.remedies:
            self.print_remedies(plan.remedies)

    def print_plan_summary(self, plan: FloorPlan) -> None:
        """Print floor plan summary panel."""
        summary = (
            f"Plot Size: {plan.width} x {plan.length} ft ({plan.total_area:.0f} sq ft)\n"
            f"Configuration: {plan.config.upper()}\n"
            f"Entrance: {plan.entrance_direction.value.title()}\n"
            f"Rooms: {len(plan.rooms)}\n"
            f"Used Area: {plan.used_area:.0f} sq ft ({plan.utilization:.1f}%)\n"
        )
        if plan.vastu_score:
            summary += f"Vastu Score: {plan.vastu_score.overall_score}/100 ({plan.vastu_score.grade})"
        self.console.print(Panel(summary, title="Floor Plan Summary", border_style="blue"))

    def print_room_layout(self, plan: FloorPlan) -> None:
        """Print room layout table."""
        table = Table(title="Room Layout")
        table.add_column("Room", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Position (x, y)", justify="right")
        table.add_column("Size (W x L)", justify="right")
        table.add_column("Area (sq ft)", justify="right")
        table.add_column("Direction", style="yellow")

        for room in plan.rooms:
            table.add_row(
                room.name,
                room.room_type.value,
                f"({room.x:.0f}, {room.y:.0f})",
                f"{room.width:.0f} x {room.length:.0f}",
                f"{room.area:.0f}",
                room.direction.value.title(),
            )

        self.console.print(table)

    def print_vastu_score(self, score: VastuScore) -> None:
        """Print Vastu score summary."""
        grade_color = {
            "Excellent": "green",
            "Good": "blue",
            "Acceptable": "yellow",
            "Needs Improvement": "dark_orange",
            "Poor": "red",
        }.get(score.grade, "white")

        table = Table(title="Vastu Compliance Score")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", justify="right")

        table.add_row("Overall Score", f"[bold {grade_color}]{score.overall_score}/100[/]")
        table.add_row("Direction Score", f"{score.direction_score}/100")
        table.add_row("Placement Score", f"{score.placement_score}/100")
        table.add_row("Proportion Score", f"{score.proportion_score}/100")
        table.add_row("Grade", f"[bold {grade_color}]{score.grade}[/]")
        table.add_row("Rules Passed", f"{score.passed_rules}/{score.total_rules}")

        self.console.print(table)

    def print_rules_detail(self, score: VastuScore) -> None:
        """Print detailed rule-by-rule results."""
        table = Table(title="Vastu Rules Detail")
        table.add_column("ID", style="dim")
        table.add_column("Rule")
        table.add_column("Status", justify="center")
        table.add_column("Weight", justify="right")
        table.add_column("Details", style="dim")

        for rule in score.rules_checked:
            status = "[green]PASS[/]" if rule.passed else "[red]FAIL[/]"
            table.add_row(
                rule.id,
                rule.name,
                status,
                f"{rule.weight:.1f}",
                rule.details[:60],
            )

        self.console.print(table)

    def print_remedies(self, remedies: list[Remedy]) -> None:
        """Print remedy suggestions."""
        table = Table(title="Vastu Remedies")
        table.add_column("Priority", justify="center", style="bold")
        table.add_column("Rule", style="cyan")
        table.add_column("Severity", justify="center")
        table.add_column("Recommended Action")
        table.add_column("Alternative Remedy", style="dim")

        severity_colors = {
            "critical": "red",
            "high": "dark_orange",
            "medium": "yellow",
            "low": "green",
        }

        for remedy in remedies:
            color = severity_colors.get(remedy.severity, "white")
            table.add_row(
                str(remedy.priority),
                remedy.rule_name,
                f"[{color}]{remedy.severity.upper()}[/]",
                remedy.recommended_action[:80],
                remedy.alternative_remedy[:60],
            )

        self.console.print(table)

    def to_json(self, plan: FloorPlan) -> str:
        """Export plan as JSON string."""
        return plan.model_dump_json(indent=2)

    def save_json(self, plan: FloorPlan, filepath: str) -> None:
        """Save plan as JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json(plan))
