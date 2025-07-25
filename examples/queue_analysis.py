#!/usr/bin/env python3
"""
Deep dive analysis of queue buildup patterns.
"""
import sys
import os
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.queue_simulator import QueueSimulator
from examples.scenarios import WEEKDAY_BASIC_SMALL


def analyze_queue_buildup():
    """Analyze when and why queues build up."""
    scenario = WEEKDAY_BASIC_SMALL
    print(f"=== QUEUE BUILDUP ANALYSIS: {scenario.name} ===")
    print(f"2 desks, 3.0 min average service time")
    print()
    
    simulator = QueueSimulator(random_seed=42)
    
    # Generate arrivals
    arrival_times = simulator.arrival_generator.generate_arrivals(scenario)
    service_times = simulator.arrival_generator.generate_service_times(
        len(arrival_times), scenario.mean_service_time
    )
    
    print(f"Generated {len(arrival_times)} customers")
    
    # Simulate with detailed tracking
    num_desks = 2
    desk_available_times = [0.0] * num_desks
    
    print("\\nDetailed customer flow (showing problem periods):")
    
    max_wait = 0
    problem_customers = []
    
    for i in range(len(arrival_times)):
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
        
        if wait_time > max_wait:
            max_wait = wait_time
        
        # Track problem customers (wait > 10 minutes)
        if wait_time > 10.0:
            problem_customers.append({
                'customer': i,
                'arrival_time': arrival_time,
                'wait_time': wait_time,
                'service_time': service_time,
                'hour': int(arrival_time // 60) + scenario.operating_hours[0],
                'desk_busy_until': [t for t in desk_available_times]
            })
    
    print(f"Total customers with >10 min wait: {len(problem_customers)}")
    print(f"Maximum wait time found: {max_wait:.2f} minutes")
    print()
    
    if problem_customers:
        print("CUSTOMERS WITH LONG WAITS:")
        print("Customer | Hour | Arrival | Wait  | Service | Desk1 Busy | Desk2 Busy")
        print("-" * 70)
        
        for pc in problem_customers[:10]:  # Show first 10 problem customers
            hour = pc['hour']
            print(f"{pc['customer']:8d} | {hour:2d}:xx | {pc['arrival_time']:7.2f} | {pc['wait_time']:5.2f} | {pc['service_time']:7.2f} | {pc['desk_busy_until'][0]:10.2f} | {pc['desk_busy_until'][1]:10.2f}")
    
    # Analyze by hour
    print("\\nARRIVAL INTENSITY BY HOUR:")
    for hour in range(scenario.operating_hours[0], scenario.operating_hours[1]):
        hour_start = (hour - scenario.operating_hours[0]) * 60
        hour_end = hour_start + 60
        hour_arrivals = [t for t in arrival_times if hour_start <= t < hour_end]
        expected = scenario.arrival_rates.get(hour, 0)
        
        # Find average service time in this hour
        hour_indices = [i for i, t in enumerate(arrival_times) if hour_start <= t < hour_end]
        if hour_indices:
            hour_service_times = [service_times[i] for i in hour_indices]
            avg_service = np.mean(hour_service_times)
            max_service = np.max(hour_service_times)
        else:
            avg_service = max_service = 0
        
        # Calculate theoretical capacity
        theoretical_capacity = 2 * 60 / scenario.mean_service_time  # desks * minutes / avg_service_time
        
        print(f"{hour:2d}:00 | Arrivals: {len(hour_arrivals):2d} (exp: {expected:2.0f}) | Avg svc: {avg_service:.2f} | Max svc: {max_service:.2f} | Capacity: {theoretical_capacity:.1f}")
        
        if len(hour_arrivals) > theoretical_capacity * 0.8:  # > 80% of capacity
            print(f"      *** HIGH UTILIZATION HOUR - Queue likely to form ***")


if __name__ == "__main__":
    analyze_queue_buildup()
