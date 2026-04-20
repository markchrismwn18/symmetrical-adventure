# Getting Started with PP-NF NEO Tracker

## Installation

### Prerequisites
- Python 3.9+
- pip or conda

### Setup

1. Clone the repository:
```bash
git clone https://github.com/markchrismwn18/symmetrical-adventure.git
cd symmetrical-adventure
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests to verify installation:
```bash
pytest tests/ -v
```

## Quick Start

### Basic NEO Tracking

```python
from src.neo_tracker import NEOTracker, NEOObject
import numpy as np

# Initialize tracker
tracker = NEOTracker()

# Create a NEO
position = np.array([6.371e6 + 400e3, 0, 0])  # LEO altitude
velocity = np.array([0, 7660, 0])  # LEO velocity
neo = NEOObject('2024-AB1', 'Test Asteroid', position, velocity)

# Register NEO
tracker.register_neo(neo)

# Predict trajectory (365 days)
trajectory = tracker.predict_trajectory('2024-AB1', duration_days=365)

# Check for close approaches
approach = tracker.check_close_approach('2024-AB1', trajectory)
print(f"Closest approach: {approach['closest_approach_km']:.0f} km")
print(f"Risk level: {approach['risk_level']}")

# Generate report
report = tracker.export_report('neo_report.txt')
print(report)
```

### Understanding the Model

The PP-NF substrate model operates on three global constants:
- **P₀ = 0.2599 Pa** - Base pressure
- **κ = 1.0** - Fold strength calibration
- **τ(d)** - Scale-dependent reaction lag (PREM-locked from 1 nm to planetary scale)

All dynamics emerge from the conservation law: **x + y = |1|**

### Key Components

| Component | Purpose |
|-----------|---------|
| `PPNFModel` | Core physics engine with substrate pressure calculations |
| `OrbitalMechanics` | Integration of PP-NF forces with RK4 propagator |
| `NEOTracker` | High-level application for NEO catalog management |
| `NEOObject` | Individual NEO representation with trajectory tracking |

## Project Structure

```
symmetrical-adventure/
├── src/
│   ├── __init__.py
│   ├── pp_nf_model.py       # Core physics
│   ├── orbital_mechanics.py  # Propagation engine
│   ├── neo_tracker.py        # Main application
│   └── utils.py              # Helper functions
├── tests/
│   ├── test_pp_nf_model.py
│   ├── test_orbital_mechanics.py
│   └── test_neo_tracker.py
├── data/                     # NEO catalog data
├── notebooks/                # Jupyter analyses
├── docs/                     # Documentation
├── requirements.txt
└── pyproject.toml
```

## Command Line Usage

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_neo_tracker.py -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### Development

```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Configuration

Edit `pyproject.toml` or environment variables to customize:
- Integration time step (default: 1 day)
- Prediction duration (default: 365 days)
- Close approach threshold (default: 384,400 km - Moon distance)
- Model parameters (P₀, κ, SA/V ratio)

## Data Format

NEO data can be stored as JSON:

```json
{
  "neo_id": "2024-AB1",
  "name": "Test Asteroid",
  "position": [6.371e6, 0, 0],
  "velocity": [0, 7660, 0],
  "mass": 1e12
}
```

Use `utils.load_neo_data()` and `save_neo_data()` for file I/O.

## Validation Against NASA Data

To validate model accuracy:

1. Load NASA/ESA NEO ephemerides
2. Compare predicted vs observed positions
3. Calculate RMS error using `utils.rms_error()`
4. Document RMS improvements in `/data/validation/`

## Troubleshooting

**Import Errors**: Ensure you're in the correct directory and virtual environment is activated.

**Test Failures**: Run `pip install -r requirements.txt` again to ensure all dependencies match.

**Numerical Instability**: Reduce integration time step (`dt_seconds`) for better accuracy.

## Next Steps

1. **Load Real NEO Data**: Add NASA/ESA NEO catalog data to `data/`
2. **Batch Processing**: Use `tracker.batch_predict()` for entire catalog
3. **Visualization**: Create plots in `/notebooks/` using matplotlib
4. **Validation**: Compare predictions against known observation data
5. **Optimization**: Tune P₀, κ, and τ(d) for lower RMS error

## References

- PP-NF Lagrangian Derivation PDF (repository root)
- MASTER AUDIT v3.1 reports
- Saturn/Jupiter SA/V analysis documents
