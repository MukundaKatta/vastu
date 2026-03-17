"""CLI interface for Vastu floor plan generator."""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console

from vastu.generator.floor_plan import FloorPlanGenerator
from vastu.models import Direction, FloorPlan
from vastu.report import VastuReportGenerator
from vastu.vastu_rules.compliance import VastuComplianceChecker
from vastu.vastu_rules.remedies import VastuRemedyAdvisor

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Vastu - AI Floor Plan Generator with Vastu Shastra Compliance."""
    pass


@cli.command()
@click.option("--width", "-w", type=float, required=True, help="Plot width (east-west) in feet.")
@click.option("--length", "-l", type=float, required=True, help="Plot length (north-south) in feet.")
@click.option("--rooms", "-r", type=click.Choice(["1bhk", "2bhk", "3bhk", "4bhk"]), default="2bhk", help="Room configuration.")
@click.option("--entrance", "-e", type=click.Choice(["north", "east", "northeast"]), default="north", help="Entrance direction.")
@click.option("--no-optimize", is_flag=True, help="Skip space optimization.")
def generate(width: float, length: float, rooms: str, entrance: str, no_optimize: bool):
    """Generate a Vastu-compliant floor plan."""
    try:
        entrance_dir = Direction(entrance)
        generator = FloorPlanGenerator(
            width=width, length=length,
            entrance=entrance_dir,
            optimize=not no_optimize,
        )
        plan = generator.generate(room_config=rooms)

        reporter = VastuReportGenerator(console)
        reporter.print_full_report(plan)

    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.option("--plan", "-p", type=click.Path(exists=True), required=True, help="Path to floor plan JSON.")
def check(plan: str):
    """Check Vastu compliance of an existing floor plan."""
    with open(plan) as f:
        data = json.load(f)

    floor_plan = FloorPlan(**data)
    checker = VastuComplianceChecker()
    score = checker.check_compliance(floor_plan)
    floor_plan.vastu_score = score

    reporter = VastuReportGenerator(console)
    reporter.print_vastu_score(score)
    reporter.print_rules_detail(score)


@cli.command()
@click.option("--plan", "-p", type=click.Path(exists=True), required=True, help="Path to floor plan JSON.")
def remedies(plan: str):
    """Get Vastu remedy suggestions for a floor plan."""
    with open(plan) as f:
        data = json.load(f)

    floor_plan = FloorPlan(**data)
    checker = VastuComplianceChecker()
    score = checker.check_compliance(floor_plan)

    advisor = VastuRemedyAdvisor()
    remedy_list = advisor.get_remedies(floor_plan, score)

    reporter = VastuReportGenerator(console)
    reporter.print_remedies(remedy_list)


@cli.command()
@click.option("--width", "-w", type=float, required=True, help="Plot width in feet.")
@click.option("--length", "-l", type=float, required=True, help="Plot length in feet.")
@click.option("--rooms", "-r", type=click.Choice(["1bhk", "2bhk", "3bhk", "4bhk"]), default="2bhk")
@click.option("--output", "-o", type=click.Path(), help="Output JSON file path.")
def report(width: float, length: float, rooms: str, output: str):
    """Generate a full Vastu report and optionally save to JSON."""
    try:
        generator = FloorPlanGenerator(width=width, length=length)
        plan = generator.generate(room_config=rooms)

        reporter = VastuReportGenerator(console)
        reporter.print_full_report(plan)

        if output:
            reporter.save_json(plan, output)
            console.print(f"\n[green]Report saved to {output}[/]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
