"""
Multi-desk queue simulation engine.
"""
import numpy as np
from typing import List, Dict, Tuple
from collections import deque
from ..models import ScenarioConfig, Customer, Desk, SimulationResults
from .arrival_generator import ArrivalGenerator


class QueueSimulator:
    """Simulates a multi-desk queue system with time-varying parameters."""
    
    def __init__(self, random_seed: int = None):
        """Initialize the queue simulator.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.arrival_generator = ArrivalGenerator(random_seed)
        self.rng = np.random.RandomState(random_seed)
    
    def simulate(self, scenario: ScenarioConfig) -> SimulationResults:
        """Run a single simulation of the queue system.
        
        Args:
            scenario: Scenario configuration
            
        Returns:
            Simulation results
        """
        # Generate customer arrivals
        arrival_times = self.arrival_generator.generate_arrivals(scenario)
        
        if not arrival_times:
            return self._empty_results(scenario)
        
        # Generate service times
        service_times = self.arrival_generator.generate_service_times(
            len(arrival_times), scenario.mean_service_time
        )
        
        # Create customers
        customers = [
            Customer(i, arrival_time) 
            for i, arrival_time in enumerate(arrival_times)
        ]
        
        # Run simulation
        return self._run_simulation(scenario, customers, service_times)
    
    def _run_simulation(self, scenario: ScenarioConfig, 
                       customers: List[Customer], 
                       service_times: List[float]) -> SimulationResults:
        """Run the actual queue simulation.
        
        Args:
            scenario: Scenario configuration
            customers: List of customers with arrival times
            service_times: List of service times for each customer
            
        Returns:
            Simulation results
        """
        # Initialize desks - get maximum number needed
        max_desks = self._get_max_desks(scenario)
        desks = [Desk(i) for i in range(max_desks)]
        
        # Queue and tracking variables
        queue = deque()
        completed_customers = []
        queue_length_history = []
        current_time = 0.0
        
        # Process each customer arrival
        for customer, service_time in zip(customers, service_times):
            current_time = customer.arrival_time
            
            # Get available desks at current time
            available_desks = self._get_available_desks(scenario, current_time)
            active_desks = desks[:available_desks]
            
            # Check if any desk is available
            available_desk = None
            for desk in active_desks:
                if desk.is_available(current_time):
                    available_desk = desk
                    break
            
            if available_desk:
                # Serve customer immediately
                available_desk.start_service(customer, current_time, service_time)
                completed_customers.append(customer)
            else:
                # Add to queue
                queue.append((customer, service_time))
            
            # Process queue - serve customers as desks become available
            self._process_queue(queue, active_desks, completed_customers, current_time)
            
            # Record queue length
            queue_length_history.append(len(queue))
        
        # Process remaining customers in queue
        while queue:
            # Find next available desk time
            available_desks = self._get_available_desks(scenario, current_time)
            active_desks = desks[:available_desks]
            
            next_available_time = min(desk.next_available_time for desk in active_desks)
            current_time = max(current_time, next_available_time)
            
            self._process_queue(queue, active_desks, completed_customers, current_time)
            queue_length_history.append(len(queue))
        
        # Calculate results
        return self._calculate_results(scenario, completed_customers, desks, queue_length_history)
    
    def _get_max_desks(self, scenario: ScenarioConfig) -> int:
        """Get the maximum number of desks needed throughout the day."""
        if scenario.desk_schedule:
            return max(scenario.desk_schedule.values())
        return scenario.num_desks or 1
    
    def _get_available_desks(self, scenario: ScenarioConfig, current_time: float) -> int:
        """Get number of available desks at current time."""
        if scenario.desk_schedule:
            # Convert time to hour
            start_hour = scenario.operating_hours[0]
            hour = int(current_time // 60) + start_hour
            return scenario.desk_schedule.get(hour, 1)
        return scenario.num_desks or 1
    
    def _process_queue(self, queue: deque, desks: List[Desk], 
                      completed_customers: List[Customer], current_time: float):
        """Process queue and assign customers to available desks."""
        while queue:
            # Find available desk
            available_desk = None
            for desk in desks:
                if desk.is_available(current_time):
                    available_desk = desk
                    break
            
            if not available_desk:
                break
            
            # Serve next customer in queue
            customer, service_time = queue.popleft()
            service_start_time = max(current_time, available_desk.next_available_time)
            available_desk.start_service(customer, service_start_time, service_time)
            completed_customers.append(customer)
    
    def _calculate_results(self, scenario: ScenarioConfig, 
                          customers: List[Customer], 
                          desks: List[Desk],
                          queue_length_history: List[int]) -> SimulationResults:
        """Calculate simulation results."""
        if not customers:
            return self._empty_results(scenario)
        
        # Calculate waiting times
        wait_times = [c.wait_time for c in customers if c.wait_time is not None]
        
        if not wait_times:
            return self._empty_results(scenario)
        
        avg_wait_time = np.mean(wait_times)
        max_wait_time = np.max(wait_times)
        
        # Calculate queue statistics
        avg_queue_length = np.mean(queue_length_history) if queue_length_history else 0
        max_queue_length = max(queue_length_history) if queue_length_history else 0
        
        # Calculate desk utilization
        total_simulation_time = scenario.operating_hours[1] - scenario.operating_hours[0]
        total_simulation_time_minutes = total_simulation_time * 60
        
        active_desks = [d for d in desks if d.customers_served > 0]
        if active_desks:
            desk_utilization = np.mean([d.get_utilization(total_simulation_time_minutes) 
                                      for d in active_desks])
        else:
            desk_utilization = 0.0
        
        # Calculate service level (% served within 5 minutes)
        served_within_5min = sum(1 for wt in wait_times if wt <= 5.0)
        service_level_5min = served_within_5min / len(wait_times)
        
        return SimulationResults(
            scenario_name=scenario.name,
            avg_wait_time=avg_wait_time,
            max_wait_time=max_wait_time,
            avg_queue_length=avg_queue_length,
            max_queue_length=max_queue_length,
            desk_utilization=desk_utilization,
            service_level_5min=service_level_5min,
            total_customers=len(customers),
            total_simulation_time=total_simulation_time_minutes
        )
    
    def _empty_results(self, scenario: ScenarioConfig) -> SimulationResults:
        """Return empty results for scenarios with no customers."""
        return SimulationResults(
            scenario_name=scenario.name,
            avg_wait_time=0.0,
            max_wait_time=0.0,
            avg_queue_length=0.0,
            max_queue_length=0,
            desk_utilization=0.0,
            service_level_5min=1.0,
            total_customers=0,
            total_simulation_time=(scenario.operating_hours[1] - scenario.operating_hours[0]) * 60
        )
