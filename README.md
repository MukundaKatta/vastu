# Vastu - AI Floor Plan Generator with Vastu Shastra Compliance

An intelligent floor plan generator that creates room layouts optimized for space utilization while ensuring compliance with traditional Vastu Shastra principles.

## Features

- **Floor Plan Generation**: Automatically generate room layouts for given plot dimensions
- **Vastu Shastra Compliance**: Score and validate plans against 20+ authentic Vastu rules
- **Room Placement Optimization**: Position rooms (bedroom, kitchen, bathroom, living, puja) according to directional guidelines
- **Space Optimization**: Maximize usable area while maintaining Vastu compliance
- **Remedy Suggestions**: Get actionable corrections for non-compliant designs
- **Rich Reports**: Generate detailed compliance reports with scores and recommendations

## Vastu Principles Implemented

- Kitchen placement in Southeast (Agni corner)
- Master bedroom in Southwest (stability)
- Puja/prayer room in Northeast (Ishanya corner)
- Entrance facing North or East (prosperity)
- Living room in North or East
- Bathrooms in Northwest or West
- Staircase placement rules
- Brahmasthan (center) kept open
- Slope and elevation guidelines
- And many more...

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Generate a floor plan
vastu generate --width 40 --length 50 --rooms 3bhk

# Check Vastu compliance of a plan
vastu check --plan plan.json

# Get remedy suggestions
vastu remedies --plan plan.json

# Generate full report
vastu report --width 40 --length 50 --rooms 3bhk --output report.json
```

### Python API

```python
from vastu.generator.floor_plan import FloorPlanGenerator
from vastu.vastu_rules.compliance import VastuComplianceChecker

generator = FloorPlanGenerator(width=40, length=50)
plan = generator.generate(room_config="3bhk")

checker = VastuComplianceChecker()
score = checker.check_compliance(plan)
print(f"Vastu Score: {score.overall_score}/100")
```

## Project Structure

```
src/vastu/
  cli.py              - CLI interface using Click
  models.py           - Pydantic data models
  report.py           - Report generation
  generator/
    floor_plan.py     - FloorPlanGenerator
    rooms.py          - RoomPlacer
    optimizer.py      - SpaceOptimizer
  vastu_rules/
    directions.py     - DirectionalRules
    compliance.py     - VastuComplianceChecker
    remedies.py       - VastuRemedyAdvisor
```

## Dependencies

- numpy - Numerical computations for layout optimization
- pydantic - Data validation and models
- click - CLI framework
- rich - Terminal formatting and tables

## Author

Mukunda Katta

## License

MIT
