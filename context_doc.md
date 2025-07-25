# Click & Collect Queue Simulation System - Project Context

## Project Overview
Building a Monte Carlo simulation system to optimize staffing for retail click & collect desks. The system predicts average and maximum waiting times based on customer arrival patterns, staffing levels, and service times.

## Architecture
- **Backend**: Python-based Monte Carlo simulation engine
- **Frontend**: Web application for scenario analysis
- **Deployment**: Web-accessible interface for retail managers

## Core Components

### 1. Simulation Engine
- **Customer Arrival Model**: Time-varying Poisson process with hourly rate changes
- **Queue System**: Multi-server queueing model (M(t)/M/c queue)
- **Service Process**: Exponential service times with configurable mean
- **Monte Carlo**: Multiple simulation runs for statistical confidence

### 2. Key Metrics
- Average waiting time per customer
- Maximum waiting time during simulation
- Queue length statistics
- Server utilization rates
- Service level percentages (e.g., % served within 5 minutes)

### 3. Scenario Parameters
- **Arrival Rates**: Hourly customer arrival rates (λ_h for each hour h)
- **Desk Staffing**: Number of available desks - constant by default, optionally time-varying
- **Service Times**: Mean service time per customer (2-15 minutes typical)
- **Operating Hours**: Store opening/closing times
- **Day Types**: Weekday vs weekend patterns

## Data Structures

### Arrival Pattern
```python
# Hourly arrival rates for a typical day
arrival_rates = {
    9: 5,   # 9-10am: 5 customers/hour
    10: 12, # 10-11am: 12 customers/hour
    11: 25, # 11-12pm: 25 customers/hour
    # ... continue for all operating hours
}
```

### Scenario Configuration
```python
# Simple scenario with constant desk staffing
scenario_simple = {
    'name': 'Peak Day - 3 Desks',
    'arrival_rates': arrival_rates,
    'num_desks': 3,              # Constant throughout day
    'mean_service_time': 8.5,    # minutes
    'operating_hours': (9, 18),  # 9am to 6pm
    'num_simulations': 1000
}

# Advanced scenario with time-varying desk staffing
scenario_advanced = {
    'name': 'Peak Day - Variable Desks',
    'arrival_rates': arrival_rates,
    'desk_schedule': {            # Optional: overrides num_desks
        9: 2,   # 9-10am: 2 desks
        10: 2,  # 10-11am: 2 desks  
        11: 4,  # 11-12pm: 4 desks (lunch rush)
        12: 4,  # 12-1pm: 4 desks
        13: 3,  # 1-2pm: 3 desks
        14: 2,  # 2-3pm: 2 desks
        # ... continue for all hours
    },
    'mean_service_time': 8.5,
    'operating_hours': (9, 18),
    'num_simulations': 1000
}
```

### Simulation Results
```python
results = {
    'avg_wait_time': 4.2,      # minutes
    'max_wait_time': 18.7,     # minutes
    'avg_queue_length': 2.1,
    'desk_utilization': 0.73,  # Average across all desks
    'service_level_5min': 0.85, # % served within 5 min
    'confidence_intervals': {...}
}
```

## Technical Requirements

### Backend (Python)
- **Core Libraries**: numpy, scipy, pandas, matplotlib
- **Simulation**: Custom discrete-event simulation or SimPy
- **API Framework**: FastAPI for web interface integration
- **Data Validation**: Pydantic models for input validation
- **Performance**: Multiprocessing for parallel Monte Carlo runs

### Frontend (Web App)
- **Framework**: Streamlit, Dash, or React/Flask
- **Visualization**: Plotly for interactive charts
- **UI Components**: Parameter input forms, results dashboard
- **Export**: PDF reports, CSV data export

### Key Algorithms

#### 1. Customer Arrival Generation
```python
def generate_arrivals(arrival_rates, operating_hours):
    """Generate customer arrival times using time-varying Poisson process"""
    # For each hour, generate Poisson arrivals
    # Return sorted list of arrival times
```

#### 2. Queue Simulation
```python
def simulate_queue(arrivals, desk_schedule, service_time_dist):
    """Simulate multi-desk queue with given arrivals and desk availability"""
    # Handle both constant desk count and time-varying schedules
    # Track: arrival times, service start times, departure times
    # Calculate: waiting times, queue lengths, desk utilization
```

#### 3. Monte Carlo Runner
```python
def run_monte_carlo(scenario, num_runs=1000):
    """Run multiple simulations and aggregate results"""
    # Generate statistical summary with confidence intervals
```

## Implementation Phases

### Phase 1: Core Simulation Backend
- Implement time-varying Poisson arrival generation
- Build multi-desk queue simulation with constant and variable desk scheduling
- Create Monte Carlo runner with parallel processing
- Add comprehensive result statistics and validation

### Phase 2: API Layer
- FastAPI endpoints for scenario execution
- Request/response models with Pydantic
- Support both simple (constant desks) and advanced (time-varying desks) scenarios
- Error handling and input validation
- Async processing for long-running simulations

### Phase 3: Web Interface
- Parameter input forms (arrival rates, desk staffing, service times)
- Toggle between constant and time-varying desk modes
- Real-time simulation progress tracking
- Interactive results visualization
- Scenario comparison capabilities
- Export functionality for reports

### Phase 4: Deployment
- Containerization with Docker
- Cloud deployment (AWS, Heroku, or similar)
- Performance optimization for web use
- User authentication and session management

## Code Style Guidelines
- **Functions**: Descriptive names, comprehensive docstrings
- **Classes**: Clear separation of concerns, inheritance where appropriate
- **Error Handling**: Specific exceptions with informative messages
- **Testing**: Unit tests for core simulation functions
- **Documentation**: Inline comments for complex algorithms

## Performance Targets
- Single scenario simulation: < 5 seconds for 1000 runs
- Web interface responsiveness: < 2 seconds for parameter updates
- Concurrent users: Support 10+ simultaneous simulations
- Accuracy: 95% confidence intervals for all key metrics

## Business Context
- **Users**: Retail store managers, operations analysts
- **Use Cases**: Daily staffing decisions, peak period planning, service level optimization, desk scheduling optimization
- **Value**: Reduce customer wait times, optimize labor costs, improve service quality, flexible staffing strategies
- **Constraints**: Real-world service time variability, unpredictable demand spikes

This system helps retail managers make data-driven staffing decisions by modeling the complex interactions between customer arrival patterns, service capacity, and operational efficiency.