# 🛒 Click & Collect Queue Simulation System

A Monte Carlo simulation system to optimize staffing for retail click & collect desks. The system predicts average and maximum waiting times based on customer arrival patterns, staffing levels, and service times.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

- **Time-varying Poisson process** for realistic customer arrivals
- **Multi-server queueing model** (M(t)/M/c queue) with exponential service times
- **Variable desk staffing** - both constant and time-varying schedules
- **Monte Carlo simulation** with parallel processing and statistical confidence intervals
- **Interactive web interface** built with Streamlit
- **Terminal-based runner** for quick scenario analysis
- **Comprehensive metrics**: wait times, service levels, utilization, queue statistics

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/YOUR_USERNAME/service_desk_simulator.git
cd service_desk_simulator
pip install -r requirements.txt
```

### Web Interface (Recommended)
```bash
python launch.py
```
Opens interactive web interface at http://localhost:8501

### Terminal Interface
```bash
# Run all scenarios with comparison
python examples/run_scenarios.py all

# Interactive single scenario selection
python examples/run_scenarios.py

# List available scenarios
python examples/run_scenarios.py list
```

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Python API
```python
from src.simulation.monte_carlo import MonteCarloRunner
from examples.scenarios import WEEKDAY_BASIC_LARGE

# Run simulation with predefined scenario
runner = MonteCarloRunner()
results = runner.run_simulation(WEEKDAY_BASIC_LARGE)
print(f"Average wait time: {results.avg_wait_time:.2f} minutes")
```

### Custom Scenarios
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

## 📊 Example Results

```
SCENARIO COMPARISON SUMMARY
==============================================================================================================
Scenario                  Avg Wait   Max Wait   Service Level  Utilization  Customers   
--------------------------------------------------------------------------------------------------------------
Weekday Basic - 3 Desks     0.39 min  14.54 min      97.0%      21.7%      156
Weekday Basic - 2 Desks     3.00 min  45.75 min      88.5%      24.3%      117
Peak Day - Variable Staf    4.47 min  36.31 min      77.4%      54.1%      779
Weekend - Steady Flow       0.21 min  10.86 min      98.5%      17.8%      128
Efficient Service - 3 De    0.10 min   7.02 min      99.2%      14.5%      156
```

## 🏗️ Project Structure

```
├── src/                    # Core simulation engine
│   ├── models.py          # Pydantic data models and validation
│   └── simulation/        # Simulation components
│       ├── arrival_generator.py   # Time-varying Poisson arrivals
│       ├── queue_simulator.py     # Multi-server queue simulation
│       └── monte_carlo.py         # Monte Carlo runner with parallel processing
├── app/                   # Streamlit web interface
│   └── main.py           # Interactive web application
├── examples/              # Example scenarios and usage
│   ├── scenarios.py      # Predefined scenarios for different store types
│   ├── run_scenarios.py  # Terminal-based scenario runner
│   └── basic_usage.py    # Simple API usage examples
├── tests/                 # Unit tests
└── launch.py             # Quick launch script
```

## 📈 Key Metrics

- **Average & Maximum Wait Times** - Customer experience indicators
- **Service Level** - Percentage of customers served within 5 minutes
- **Desk Utilization** - Staff efficiency and capacity planning
- **Queue Statistics** - Average and maximum queue lengths
- **Statistical Confidence** - 95% confidence intervals for all metrics

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/test_models.py -v
```

## 📋 Requirements

- Python 3.13+
- NumPy, SciPy, Pandas
- Pydantic for data validation
- Streamlit for web interface
- Plotly for visualizations
- pytest for testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for retail operations optimization
- Uses queueing theory and Monte Carlo methods
- Designed for real-world click & collect scenarios

See `context_doc.md` for detailed project context and technical specifications.
