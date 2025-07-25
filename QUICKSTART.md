# Quick Start Guide

## Installation

1. **Clone or set up the project directory**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Method 1: Web Interface (Recommended)
```bash
python launch.py
```
This will start the Streamlit web interface at http://localhost:8501

### Method 2: Command Line Example
```bash
python examples/basic_usage.py
```

### Method 3: Python Script
```python
from src.simulation.monte_carlo import MonteCarloRunner
from examples.scenarios import WEEKDAY_BASIC

runner = MonteCarloRunner()
results = runner.run_simulation(WEEKDAY_BASIC)
print(f"Average wait time: {results.avg_wait_time:.2f} minutes")
```

## Running Tests
```bash
python -m pytest tests/
```

## Project Structure
```
├── src/                    # Core simulation engine
│   ├── models.py          # Data models and validation
│   └── simulation/        # Simulation components
├── app/                   # Web interface
├── examples/              # Example scenarios and usage
├── tests/                 # Unit tests
└── launch.py             # Quick launch script
```

## Key Features
- Time-varying Poisson arrival process
- Multi-server queue simulation
- Support for constant and variable desk staffing
- Monte Carlo analysis with confidence intervals
- Interactive web interface
- Predefined and custom scenarios
