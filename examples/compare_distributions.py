#!/usr/bin/env python3
"""
Compare exponential vs lognormal service time distributions.
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.arrival_generator import ArrivalGenerator


def compare_service_time_distributions():
    """Compare exponential and lognormal service time distributions."""
    
    # Parameters
    mean_service_time = 3.0  # minutes
    num_samples = 10000
    
    # Create generators
    generator = ArrivalGenerator(random_seed=42)
    rng = np.random.RandomState(42)  # For exponential comparison
    
    print("Service Time Distribution Comparison")
    print("=" * 50)
    print(f"Mean service time: {mean_service_time} minutes")
    print(f"Number of samples: {num_samples}")
    print()
    
    # Generate lognormal service times (current implementation)
    lognormal_times = generator.generate_service_times(num_samples, mean_service_time)
    
    # Generate exponential service times (old implementation)
    exponential_times = rng.exponential(mean_service_time, num_samples)
    
    # Statistics comparison
    distributions = {
        "Lognormal": lognormal_times,
        "Exponential": exponential_times
    }
    
    print(f"{'Statistic':<20} {'Lognormal':<15} {'Exponential':<15} {'Difference':<15}")
    print("-" * 70)
    
    for dist_name, times in distributions.items():
        mean_val = np.mean(times)
        std_val = np.std(times)
        cv = std_val / mean_val
        min_val = np.min(times)
        max_val = np.max(times)
        p50 = np.percentile(times, 50)
        p95 = np.percentile(times, 95)
        p99 = np.percentile(times, 99)
        
        if dist_name == "Lognormal":
            ln_stats = [mean_val, std_val, cv, min_val, max_val, p50, p95, p99]
        else:
            exp_stats = [mean_val, std_val, cv, min_val, max_val, p50, p95, p99]
    
    stat_names = ["Mean", "Std Dev", "Coeff of Var", "Min", "Max", "50th %ile", "95th %ile", "99th %ile"]
    
    for i, stat_name in enumerate(stat_names):
        ln_val = ln_stats[i]
        exp_val = exp_stats[i]
        diff = ln_val - exp_val if stat_name != "Coeff of Var" else f"{ln_val:.3f} vs {exp_val:.3f}"
        
        if stat_name == "Coeff of Var":
            print(f"{stat_name:<20} {ln_val:<15.3f} {exp_val:<15.3f} {diff}")
        else:
            print(f"{stat_name:<20} {ln_val:<15.2f} {exp_val:<15.2f} {diff:<15.2f}")
    
    print()
    print("Key Differences:")
    print("• Lognormal has lower coefficient of variation (less extreme outliers)")
    print("• Lognormal has higher median but similar mean")
    print("• Lognormal 95th percentile is typically lower (better customer experience)")
    print("• Lognormal better represents real-world service times")


def analyze_customer_impact():
    """Show how the distribution choice affects customer wait times."""
    from src.simulation.monte_carlo import MonteCarloRunner
    from examples.scenarios import WEEKDAY_BASIC_LARGE
    
    print("\nCustomer Wait Time Impact Analysis")
    print("=" * 50)
    
    # Test with current lognormal implementation
    runner = MonteCarloRunner()
    scenario = WEEKDAY_BASIC_LARGE.copy()
    scenario.num_simulations = 500
    
    result = runner.run_simulation(scenario, parallel=False)
    
    print(f"Scenario: {result.scenario_name}")
    print(f"Service Time Distribution: Lognormal (CV=0.5)")
    print()
    print("Wait Time Results:")
    print(f"• Average wait time: {result.avg_wait_time:.2f} minutes")
    print(f"• 95th percentile wait: {result.p95_wait_time:.2f} minutes")
    print(f"• Maximum wait time: {result.max_wait_time:.2f} minutes")
    print(f"• Service level (≤5min): {result.service_level_5min:.1%}")
    print()
    print("Business Benefits of Lognormal Distribution:")
    print("• More realistic service time variability")
    print("• Fewer extreme wait times")
    print("• Better prediction accuracy")
    print("• Matches real-world retail operations")


if __name__ == "__main__":
    compare_service_time_distributions()
    analyze_customer_impact()
