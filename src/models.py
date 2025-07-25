"""
Data models for the queue simulation system using Pydantic for validation.
"""
from typing import Dict, Optional, Tuple, Union
from pydantic import BaseModel, Field, validator
import numpy as np


class ScenarioConfig(BaseModel):
    """Configuration for a simulation scenario."""
    
    name: str = Field(..., description="Descriptive name for the scenario")
    arrival_rates: Dict[int, float] = Field(..., description="Hourly arrival rates (hour -> customers/hour)")
    num_desks: Optional[int] = Field(None, description="Constant number of desks (if not using desk_schedule)")
    desk_schedule: Optional[Dict[int, int]] = Field(None, description="Time-varying desk schedule (hour -> num_desks)")
    mean_service_time: float = Field(..., gt=0, description="Mean service time in minutes")
    operating_hours: Tuple[int, int] = Field(..., description="Operating hours as (start_hour, end_hour)")
    num_simulations: int = Field(1000, gt=0, description="Number of Monte Carlo simulation runs")
    
    @validator('operating_hours')
    def validate_operating_hours(cls, v):
        start, end = v
        if start >= end or start < 0 or end > 24:
            raise ValueError("Invalid operating hours: start must be < end, both must be 0-24")
        return v
    
    @validator('arrival_rates')
    def validate_arrival_rates(cls, v):
        for hour, rate in v.items():
            if hour < 0 or hour > 23:
                raise ValueError(f"Invalid hour {hour}: must be 0-23")
            if rate < 0:
                raise ValueError(f"Invalid arrival rate {rate}: must be >= 0")
        return v
    
    @validator('desk_schedule')
    def validate_desk_schedule(cls, v, values):
        if v is not None and 'num_desks' in values and values['num_desks'] is not None:
            raise ValueError("Cannot specify both num_desks and desk_schedule")
        if v is not None:
            for hour, desks in v.items():
                if hour < 0 or hour > 23:
                    raise ValueError(f"Invalid hour {hour}: must be 0-23")
                if desks < 1:
                    raise ValueError(f"Invalid desk count {desks}: must be >= 1")
        return v
    
    def get_desk_count(self, hour: int) -> int:
        """Get the number of desks available at a given hour."""
        if self.desk_schedule is not None:
            return self.desk_schedule.get(hour, 1)
        return self.num_desks or 1


class Customer:
    """Represents a customer in the queue system."""
    
    def __init__(self, customer_id: int, arrival_time: float):
        self.customer_id = customer_id
        self.arrival_time = arrival_time
        self.service_start_time: Optional[float] = None
        self.departure_time: Optional[float] = None
    
    @property
    def wait_time(self) -> Optional[float]:
        """Calculate waiting time in minutes."""
        if self.service_start_time is None:
            return None
        return self.service_start_time - self.arrival_time
    
    @property
    def service_time(self) -> Optional[float]:
        """Calculate service time in minutes."""
        if self.service_start_time is None or self.departure_time is None:
            return None
        return self.departure_time - self.service_start_time
    
    @property
    def total_time(self) -> Optional[float]:
        """Calculate total time in system in minutes."""
        if self.departure_time is None:
            return None
        return self.departure_time - self.arrival_time


class Desk:
    """Represents a service desk."""
    
    def __init__(self, desk_id: int):
        self.desk_id = desk_id
        self.current_customer: Optional[Customer] = None
        self.next_available_time: float = 0.0
        self.total_service_time: float = 0.0
        self.customers_served: int = 0
    
    def is_available(self, time: float) -> bool:
        """Check if desk is available at given time."""
        return time >= self.next_available_time
    
    def start_service(self, customer: Customer, start_time: float, service_duration: float):
        """Start serving a customer."""
        self.current_customer = customer
        customer.service_start_time = start_time
        customer.departure_time = start_time + service_duration
        self.next_available_time = customer.departure_time
        self.total_service_time += service_duration
        self.customers_served += 1
    
    def get_utilization(self, total_time: float) -> float:
        """Calculate desk utilization rate."""
        if total_time <= 0:
            return 0.0
        return min(1.0, self.total_service_time / total_time)


class SimulationResults(BaseModel):
    """Results from a single simulation run."""
    
    scenario_name: str
    avg_wait_time: float = Field(..., description="Average waiting time in minutes")
    max_wait_time: float = Field(..., description="Maximum waiting time in minutes")
    avg_queue_length: float = Field(..., description="Average queue length")
    max_queue_length: int = Field(..., description="Maximum queue length")
    desk_utilization: float = Field(..., description="Average desk utilization rate")
    service_level_5min: float = Field(..., description="Percentage served within 5 minutes")
    total_customers: int = Field(..., description="Total number of customers served")
    total_simulation_time: float = Field(..., description="Total simulation time in minutes")


class MonteCarloResults(BaseModel):
    """Aggregated results from multiple simulation runs."""
    
    scenario_name: str
    num_simulations: int
    
    # Average metrics
    avg_wait_time: float
    max_wait_time: float
    avg_queue_length: float
    desk_utilization: float
    service_level_5min: float
    
    # Confidence intervals (95%)
    avg_wait_time_ci: Tuple[float, float]
    max_wait_time_ci: Tuple[float, float]
    avg_queue_length_ci: Tuple[float, float]
    desk_utilization_ci: Tuple[float, float]
    service_level_5min_ci: Tuple[float, float]
    
    # Additional statistics
    total_customers_mean: float
    total_customers_std: float
