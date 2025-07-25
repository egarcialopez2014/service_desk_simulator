#!/usr/bin/env python3
"""
Diagnostic script to analyze maximum waiting times in detail.
"""
import sys
import os
import numpy as np

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.queue_simulator import QueueSimulator
from src.simulation.arrival_generator import ArrivalGenerator
from examples.scenarios import WEEKDAY_BASIC_SMALL, PEAKSEASON_DAY_VARIABLE


def analyze_wait_times(scenario, num_runs=5):
    """Analyze wait times in detail for a scenario."""
    print(f"=== ANALYZING: {scenario.name} ===")
    print(f"Operating hours: {scenario.operating_hours[0]}:00 - {scenario.operating_hours[1]}:00")
    print(f"Desks: {scenario.num_desks if scenario.num_desks else 'Variable'}")
    print(f"Service time: {scenario.mean_service_time} minutes")
    print()
    
    simulator = QueueSimulator(random_seed=42)
    
    for run in range(num_runs):
        print(f"--- Run {run + 1} ---")
        
        # Generate arrivals and service times
        arrival_times = simulator.arrival_generator.generate_arrivals(scenario)
        service_times = simulator.arrival_generator.generate_service_times(
            len(arrival_times), scenario.mean_service_time
        )
        
        print(f"Total arrivals: {len(arrival_times)}")
        if arrival_times:
            print(f"First arrival: {arrival_times[0]:.2f} min ({arrival_times[0]/60:.2f} hours)")
            print(f"Last arrival: {arrival_times[-1]:.2f} min ({arrival_times[-1]/60:.2f} hours)")
            print(f"Peak arrival period: {np.percentile(arrival_times, 75):.2f} - {np.percentile(arrival_times, 95):.2f} min")
        
        # Run simulation with detailed tracking
        customers = [
            simulator._create_customer(i, arrival_time) 
            for i, arrival_time in enumerate(arrival_times)
        ]
        
        # Simulate (this is a simplified version to see what happens)
        result = simulator.simulate(scenario)
        
        # Find customers with highest wait times
        completed_customers = []
        # We need to access the customers after simulation - let me modify this
        
        print(f"Average wait time: {result.avg_wait_time:.2f} minutes")
        print(f"Maximum wait time: {result.max_wait_time:.2f} minutes")
        print(f"Service level (≤5min): {result.service_level_5min:.1%}")
        print()


def detailed_single_run_analysis(scenario):
    """Run a single simulation with detailed customer tracking."""
    print(f"=== DETAILED ANALYSIS: {scenario.name} ===")
    
    # Create a simulator
    simulator = QueueSimulator(random_seed=42)
    
    # Generate arrivals
    arrival_times = simulator.arrival_generator.generate_arrivals(scenario)
    service_times = simulator.arrival_generator.generate_service_times(
        len(arrival_times), scenario.mean_service_time
    )
    
    print(f"Generated {len(arrival_times)} customers")
    
    if not arrival_times:
        print("No customers generated!")
        return
    
    # Show arrival pattern
    print("\nArrival pattern by hour:")
    operating_start = scenario.operating_hours[0]
    for hour_offset in range(scenario.operating_hours[1] - scenario.operating_hours[0]):
        hour_start = hour_offset * 60
        hour_end = (hour_offset + 1) * 60
        hour_arrivals = [t for t in arrival_times if hour_start <= t < hour_end]
        actual_hour = operating_start + hour_offset
        expected_rate = scenario.arrival_rates.get(actual_hour, 0)
        print(f"  {actual_hour:2d}:00-{actual_hour+1:2d}:00: {len(hour_arrivals):3d} customers (expected: {expected_rate})")
    
    print(f"\nService time stats: mean={np.mean(service_times):.2f}, max={np.max(service_times):.2f} min")
    
    # Simple simulation to show the queue buildup
    print("\nSimulating customer flow...")
    
    if scenario.num_desks:
        num_desks = scenario.num_desks
    else:
        num_desks = max(scenario.desk_schedule.values()) if scenario.desk_schedule else 3
    
    print(f"Using {num_desks} desks")
    
    desk_available_times = [0.0] * num_desks
    max_wait_encountered = 0.0
    max_wait_customer = None
    queue_lengths = []
    
    # Process first 50 customers to show the pattern
    customers_to_show = min(50, len(arrival_times))
    
    for i in range(customers_to_show):
        arrival_time = arrival_times[i]
        service_time = service_times[i]
        
        # Find earliest available desk
        earliest_desk = min(range(num_desks), key=lambda d: desk_available_times[d])
        earliest_available_time = desk_available_times[earliest_desk]
        
        # When can this customer start service?
        service_start_time = max(arrival_time, earliest_available_time)
        wait_time = service_start_time - arrival_time
        
        # Update desk availability
        desk_available_times[earliest_desk] = service_start_time + service_time
        
        # Count how many desks are busy at arrival time
        busy_desks = sum(1 for t in desk_available_times if t > arrival_time)
        queue_lengths.append(max(0, busy_desks - num_desks))
        
        if wait_time > max_wait_encountered:
            max_wait_encountered = wait_time
            max_wait_customer = i
        
        # Show customers with significant waits or first few
        if i < 10 or wait_time > 5.0:
            print(f"  Customer {i:2d}: arrival={arrival_time:6.2f}, wait={wait_time:6.2f} min, service={service_time:5.2f} min, busy_desks={busy_desks}")
    
    print(f"\nIn first {customers_to_show} customers:")
    print(f"  Maximum wait time: {max_wait_encountered:.2f} minutes (customer {max_wait_customer})")
    print(f"  Average queue length: {np.mean(queue_lengths):.2f}")
    print(f"  Maximum queue length: {max(queue_lengths)}")
    
    # Run full simulation for comparison
    result = simulator.simulate(scenario)
    print(f"\nFull simulation results:")
    print(f"  Average wait time: {result.avg_wait_time:.2f} minutes")
    print(f"  Maximum wait time: {result.max_wait_time:.2f} minutes")
    print(f"  Total customers: {result.total_customers}")
    
    # Explain why max wait times can be high
    print(f"\nWhy maximum wait times are high:")
    print(f"  1. Peak arrival periods create queues")
    print(f"  2. Service times are exponentially distributed (some very long)")
    print(f"  3. Random clustering of arrivals")
    print(f"  4. Once a queue forms, it takes time to clear")


def main():
    """Main analysis function."""
    print("MAXIMUM WAIT TIME ANALYSIS")
    print("=" * 60)
    print()
    
    # Analyze the scenarios that showed high max wait times
    print("The maximum wait time is calculated as:")
    print("  max_wait_time = max(service_start_time - arrival_time for all customers)")
    print()
    print("High wait times occur when:")
    print("  1. All desks are busy (high utilization)")
    print("  2. Customers arrive in clusters (Poisson randomness)")
    print("  3. Some customers get unlucky with long service times ahead of them")
    print()
    
    # Analyze small store scenario (showed 45+ min max wait)
    detailed_single_run_analysis(WEEKDAY_BASIC_SMALL)
    
    print("\\n" + "="*60 + "\\n")
    
    # Analyze peak scenario
    detailed_single_run_analysis(PEAKSEASON_DAY_VARIABLE)


if __name__ == "__main__":
    main()
