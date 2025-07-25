# Click & Collect Queue Simulation System

A Monte Carlo simulation system to optimize staffing for retail click & collect desks. The system predicts average and maximum waiting times based on customer arrival patterns, staffing levels, and service times.

## Features

- Time-varying Poisson process for customer arrivals
- Multi-server queueing model (M(t)/M/c queue)
- Support for both constant and time-varying desk staffing
- Monte Carlo simulation with statistical confidence intervals
- Web interface for scenario analysis
- Interactive visualization and reporting

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run a basic simulation:
```python
from src.simulation.monte_carlo import MonteCarloRunner
from examples.scenarios import WEEKDAY_BASIC_LARGE

# Run simulation with predefined scenario
runner = MonteCarloRunner()
results = runner.run_simulation(WEEKDAY_BASIC_LARGE)
print(f"Average wait time: {results.avg_wait_time:.2f} minutes")
```

Or create a custom scenario:
```python
from src.models import ScenarioConfig
from src.simulation.monte_carlo import MonteCarloRunner

# Define custom scenario
scenario = ScenarioConfig(
    name='Custom Test',
    arrival_rates={10: 5, 11: 12, 12: 25, 13: 30, 14: 20, 15: 15, 16: 10, 17: 8, 18: 5},
    num_desks=3,
    mean_service_time=8.5,
    operating_hours=(10, 19),
    num_simulations=100
)

# Run simulation
runner = MonteCarloRunner()
results = runner.run_simulation(scenario)
print(f"Average wait time: {results.avg_wait_time:.2f} minutes")
```

3. Launch web interface:
```bash
streamlit run app/main.py
```

## Project Structure

- `src/` - Core simulation engine
- `app/` - Web interface
- `tests/` - Unit tests
- `examples/` - Example scenarios and usage

## Documentation

See `context_doc.md` for detailed project context and technical specifications.
