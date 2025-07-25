"""
Click & Collect Queue Simulation System

A Monte Carlo simulation system for optimizing retail click & collect desk staffing.
"""

__version__ = "1.0.0"
__author__ = "Service Desk Simulator"

from .models import ScenarioConfig, SimulationResults, MonteCarloResults, Customer, Desk

__all__ = [
    "ScenarioConfig", 
    "SimulationResults", 
    "MonteCarloResults", 
    "Customer", 
    "Desk"
]
