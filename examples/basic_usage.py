"""
Basic usage example for the Click & Collect Queue Simulation System.
"""
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.monte_carlo import MonteCarloRunner
from examples.scenarios import WEEKDAY_BASIC_LARGE, PEAKSEASON_DAY_VARIABLE


def main():
    """Run basic simulation examples."""
    print("Click & Collect Queue Simulation System")
    print("=" * 50)
    
    # Initialize Monte Carlo runner
    runner = MonteCarloRunner()
    
    # Run basic weekday scenario
    print(f"\nRunning scenario: {WEEKDAY_BASIC_LARGE.name}")
    print("This may take a few moments...")
    
    try:
        results_basic = runner.run_simulation(WEEKDAY_BASIC_LARGE)
        print(runner.generate_report(results_basic))
        
        # Run variable staffing scenario
        print(f"\nRunning scenario: {PEAKSEASON_DAY_VARIABLE.name}")
        print("This may take a few moments...")
        
        results_variable = runner.run_simulation(PEAKSEASON_DAY_VARIABLE)
        print(runner.generate_report(results_variable))
        
        # Compare scenarios
        print("\nScenario Comparison:")
        print("-" * 50)
        print(f"{'Metric':<25} {'Basic (3 desks)':<15} {'Variable desks':<15}")
        print("-" * 55)
        print(f"{'Avg Wait Time (min)':<25} {results_basic.avg_wait_time:<15.2f} {results_variable.avg_wait_time:<15.2f}")
        print(f"{'Max Wait Time (min)':<25} {results_basic.max_wait_time:<15.2f} {results_variable.max_wait_time:<15.2f}")
        print(f"{'Desk Utilization':<25} {results_basic.desk_utilization:<15.1%} {results_variable.desk_utilization:<15.1%}")
        print(f"{'Service Level (≤5min)':<25} {results_basic.service_level_5min:<15.1%} {results_variable.service_level_5min:<15.1%}")
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()
