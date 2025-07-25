"""
Customer arrival generation using time-varying Poisson process.
"""
import numpy as np
from typing import Dict, List, Tuple
from ..models import ScenarioConfig


class ArrivalGenerator:
    """Generates customer arrival times using time-varying Poisson process."""
    
    def __init__(self, random_seed: int = None):
        """Initialize the arrival generator.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(random_seed)
    
    def generate_arrivals(self, scenario: ScenarioConfig) -> List[float]:
        """Generate customer arrival times for a scenario.
        
        Args:
            scenario: Scenario configuration containing arrival rates and operating hours
            
        Returns:
            List of arrival times in minutes from start of operating hours
        """
        arrivals = []
        start_hour, end_hour = scenario.operating_hours
        
        for hour in range(start_hour, end_hour):
            if hour in scenario.arrival_rates:
                rate = scenario.arrival_rates[hour]
                hour_arrivals = self._generate_hour_arrivals(hour - start_hour, rate)
                arrivals.extend(hour_arrivals)
        
        return sorted(arrivals)
    
    def _generate_hour_arrivals(self, hour_offset: int, rate: float) -> List[float]:
        """Generate arrivals for a single hour using Poisson process.
        
        Args:
            hour_offset: Hour offset from start of operating hours
            rate: Arrival rate (customers per hour)
            
        Returns:
            List of arrival times within the hour
        """
        if rate <= 0:
            return []
        
        # Generate number of arrivals for this hour using Poisson distribution
        num_arrivals = self.rng.poisson(rate)
        
        if num_arrivals == 0:
            return []
        
        # Generate arrival times uniformly within the hour
        hour_start = hour_offset * 60  # Convert to minutes
        arrival_times = self.rng.uniform(hour_start, hour_start + 60, num_arrivals)
        
        return arrival_times.tolist()
    
    def generate_service_times(self, num_customers: int, mean_service_time: float, 
                             coefficient_of_variation: float = 0.5) -> List[float]:
        """Generate service times using lognormal distribution.
        
        Args:
            num_customers: Number of service times to generate
            mean_service_time: Mean service time in minutes
            coefficient_of_variation: Ratio of std deviation to mean (default 0.5)
                                    Higher values = more variability
                                    
        Returns:
            List of service times in minutes
        """
        if num_customers == 0:
            return []
        
        # Use lognormal distribution with given mean and coefficient of variation
        # For lognormal: mean = exp(mu + sigma^2/2)
        # CV = sqrt(exp(sigma^2) - 1), so sigma = sqrt(ln(CV^2 + 1))
        cv = coefficient_of_variation
        sigma = np.sqrt(np.log(cv**2 + 1))
        mu = np.log(mean_service_time) - sigma**2 / 2
        
        service_times = self.rng.lognormal(mu, sigma, num_customers)
        return service_times.tolist()
    
    def validate_arrival_pattern(self, arrival_rates: Dict[int, float], 
                                operating_hours: Tuple[int, int]) -> Dict[str, float]:
        """Validate and analyze arrival pattern.
        
        Args:
            arrival_rates: Hourly arrival rates
            operating_hours: Operating hours tuple
            
        Returns:
            Dictionary with pattern statistics
        """
        start_hour, end_hour = operating_hours
        total_arrivals = 0
        peak_rate = 0
        peak_hour = None
        
        for hour in range(start_hour, end_hour):
            rate = arrival_rates.get(hour, 0)
            total_arrivals += rate
            
            if rate > peak_rate:
                peak_rate = rate
                peak_hour = hour
        
        operating_duration = end_hour - start_hour
        avg_rate = total_arrivals / operating_duration if operating_duration > 0 else 0
        
        return {
            'total_expected_arrivals': total_arrivals,
            'peak_rate': peak_rate,
            'peak_hour': peak_hour,
            'average_rate': avg_rate,
            'operating_hours': operating_duration
        }
