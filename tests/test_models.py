"""
Unit tests for the models module.
"""
import pytest
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import ScenarioConfig, Customer, Desk


class TestScenarioConfig:
    """Test the ScenarioConfig model."""
    
    def test_valid_scenario_config(self):
        """Test creating a valid scenario configuration."""
        config = ScenarioConfig(
            name="Test Scenario",
            arrival_rates={9: 5, 10: 10, 11: 15},
            num_desks=3,
            mean_service_time=8.5,
            operating_hours=(9, 18),
            num_simulations=100
        )
        
        assert config.name == "Test Scenario"
        assert config.num_desks == 3
        assert config.mean_service_time == 8.5
        assert config.get_desk_count(10) == 3
    
    def test_desk_schedule_scenario(self):
        """Test scenario with time-varying desk schedule."""
        config = ScenarioConfig(
            name="Variable Desks",
            arrival_rates={9: 5, 10: 10, 11: 15},
            desk_schedule={9: 2, 10: 3, 11: 4},
            mean_service_time=8.5,
            operating_hours=(9, 12),
            num_simulations=100
        )
        
        assert config.get_desk_count(9) == 2
        assert config.get_desk_count(10) == 3
        assert config.get_desk_count(11) == 4
        assert config.get_desk_count(12) == 1  # Default when not specified
    
    def test_invalid_operating_hours(self):
        """Test validation of operating hours."""
        with pytest.raises(ValueError):
            ScenarioConfig(
                name="Invalid Hours",
                arrival_rates={9: 5},
                num_desks=3,
                mean_service_time=8.5,
                operating_hours=(18, 9),  # End before start
                num_simulations=100
            )
    
    def test_invalid_arrival_rates(self):
        """Test validation of arrival rates."""
        with pytest.raises(ValueError):
            ScenarioConfig(
                name="Invalid Rates",
                arrival_rates={25: 5},  # Invalid hour
                num_desks=3,
                mean_service_time=8.5,
                operating_hours=(9, 18),
                num_simulations=100
            )
    
    def test_conflicting_desk_config(self):
        """Test that both num_desks and desk_schedule cannot be specified."""
        with pytest.raises(ValueError):
            ScenarioConfig(
                name="Conflicting Config",
                arrival_rates={9: 5},
                num_desks=3,
                desk_schedule={9: 2},  # Conflict
                mean_service_time=8.5,
                operating_hours=(9, 18),
                num_simulations=100
            )


class TestCustomer:
    """Test the Customer class."""
    
    def test_customer_creation(self):
        """Test creating a customer."""
        customer = Customer(customer_id=1, arrival_time=60.0)
        
        assert customer.customer_id == 1
        assert customer.arrival_time == 60.0
        assert customer.service_start_time is None
        assert customer.departure_time is None
        assert customer.wait_time is None
    
    def test_customer_service_timing(self):
        """Test customer service timing calculations."""
        customer = Customer(customer_id=1, arrival_time=60.0)
        
        # Start service after 5 minutes of waiting
        customer.service_start_time = 65.0
        customer.departure_time = 73.5  # 8.5 minutes of service
        
        assert customer.wait_time == 5.0
        assert customer.service_time == 8.5
        assert customer.total_time == 13.5


class TestDesk:
    """Test the Desk class."""
    
    def test_desk_creation(self):
        """Test creating a desk."""
        desk = Desk(desk_id=1)
        
        assert desk.desk_id == 1
        assert desk.current_customer is None
        assert desk.next_available_time == 0.0
        assert desk.is_available(0.0)
    
    def test_desk_service(self):
        """Test desk service operations."""
        desk = Desk(desk_id=1)
        customer = Customer(customer_id=1, arrival_time=60.0)
        
        # Start service
        desk.start_service(customer, 65.0, 8.5)
        
        assert desk.current_customer == customer
        assert desk.next_available_time == 73.5
        assert not desk.is_available(70.0)
        assert desk.is_available(74.0)
        assert desk.customers_served == 1
    
    def test_desk_utilization(self):
        """Test desk utilization calculation."""
        desk = Desk(desk_id=1)
        customer = Customer(customer_id=1, arrival_time=60.0)
        
        # Serve customer for 8.5 minutes out of 60 minute period
        desk.start_service(customer, 65.0, 8.5)
        
        utilization = desk.get_utilization(60.0)
        expected_utilization = 8.5 / 60.0
        
        assert abs(utilization - expected_utilization) < 0.001


if __name__ == "__main__":
    pytest.main([__file__])
