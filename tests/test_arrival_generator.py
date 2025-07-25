"""
Unit tests for the arrival generator.
"""
import pytest
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.arrival_generator import ArrivalGenerator
from src.models import ScenarioConfig


class TestArrivalGenerator:
    """Test the ArrivalGenerator class."""
    
    def test_arrival_generator_creation(self):
        """Test creating an arrival generator."""
        generator = ArrivalGenerator(random_seed=42)
        assert generator is not None
    
    def test_generate_arrivals_simple(self):
        """Test generating arrivals for a simple scenario."""
        generator = ArrivalGenerator(random_seed=42)
        
        scenario = ScenarioConfig(
            name="Test",
            arrival_rates={9: 10, 10: 15},  # 10 customers at 9am, 15 at 10am
            num_desks=3,
            mean_service_time=8.5,
            operating_hours=(9, 11),
            num_simulations=1
        )
        
        arrivals = generator.generate_arrivals(scenario)
        
        # Should have some arrivals (exact number varies due to Poisson randomness)
        assert len(arrivals) > 0
        
        # All arrivals should be within operating hours (0-120 minutes)
        assert all(0 <= arrival < 120 for arrival in arrivals)
        
        # Arrivals should be sorted
        assert arrivals == sorted(arrivals)
    
    def test_generate_arrivals_empty(self):
        """Test generating arrivals when rates are zero."""
        generator = ArrivalGenerator(random_seed=42)
        
        scenario = ScenarioConfig(
            name="Empty Test",
            arrival_rates={9: 0, 10: 0},  # No customers
            num_desks=3,
            mean_service_time=8.5,
            operating_hours=(9, 11),
            num_simulations=1
        )
        
        arrivals = generator.generate_arrivals(scenario)
        assert len(arrivals) == 0
    
    def test_generate_service_times(self):
        """Test generating service times."""
        generator = ArrivalGenerator(random_seed=42)
        
        service_times = generator.generate_service_times(100, 8.5)
        
        assert len(service_times) == 100
        assert all(time > 0 for time in service_times)
        
        # Mean should be approximately 8.5 (exponential distribution)
        mean_service = sum(service_times) / len(service_times)
        assert 7.0 < mean_service < 10.0  # Allow some variance
    
    def test_validate_arrival_pattern(self):
        """Test arrival pattern validation and analysis."""
        generator = ArrivalGenerator()
        
        arrival_rates = {9: 10, 10: 15, 11: 20}
        operating_hours = (9, 12)
        
        stats = generator.validate_arrival_pattern(arrival_rates, operating_hours)
        
        assert stats['total_expected_arrivals'] == 45  # 10+15+20
        assert stats['peak_rate'] == 20
        assert stats['peak_hour'] == 11
        assert stats['average_rate'] == 15.0  # 45/3 hours
        assert stats['operating_hours'] == 3


if __name__ == "__main__":
    pytest.main([__file__])
