"""
Monte Carlo simulation runner with parallel processing and statistical analysis.
"""
import numpy as np
from typing import List, Dict, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from ..models import ScenarioConfig, SimulationResults, MonteCarloResults
from .queue_simulator import QueueSimulator


def run_single_simulation(scenario_dict: dict, seed: int) -> dict:
    """Run a single simulation - used for multiprocessing.
    
    Args:
        scenario_dict: Scenario configuration as dictionary
        seed: Random seed for this simulation run
        
    Returns:
        Simulation results as dictionary
    """
    scenario = ScenarioConfig(**scenario_dict)
    simulator = QueueSimulator(random_seed=seed)
    result = simulator.simulate(scenario)
    return result.dict()


class MonteCarloRunner:
    """Runs Monte Carlo simulations with statistical analysis."""
    
    def __init__(self, max_workers: int = None):
        """Initialize the Monte Carlo runner.
        
        Args:
            max_workers: Maximum number of parallel workers (defaults to CPU count)
        """
        self.max_workers = max_workers or mp.cpu_count()
    
    def run_simulation(self, scenario: ScenarioConfig, 
                      parallel: bool = True) -> MonteCarloResults:
        """Run Monte Carlo simulation for a scenario.
        
        Args:
            scenario: Scenario configuration
            parallel: Whether to run simulations in parallel
            
        Returns:
            Aggregated Monte Carlo results with confidence intervals
        """
        if parallel and scenario.num_simulations > 1:
            results = self._run_parallel(scenario)
        else:
            results = self._run_sequential(scenario)
        
        return self._aggregate_results(scenario, results)
    
    def _run_parallel(self, scenario: ScenarioConfig) -> List[SimulationResults]:
        """Run simulations in parallel using multiprocessing."""
        scenario_dict = scenario.dict()
        seeds = np.random.randint(0, 2**31 - 1, scenario.num_simulations)
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all simulation jobs
            future_to_seed = {
                executor.submit(run_single_simulation, scenario_dict, seed): seed 
                for seed in seeds
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_seed):
                try:
                    result_dict = future.result()
                    result = SimulationResults(**result_dict)
                    results.append(result)
                except Exception as e:
                    print(f"Simulation failed with seed {future_to_seed[future]}: {e}")
        
        return results
    
    def _run_sequential(self, scenario: ScenarioConfig) -> List[SimulationResults]:
        """Run simulations sequentially."""
        results = []
        simulator = QueueSimulator()
        
        for i in range(scenario.num_simulations):
            # Use different seed for each run
            simulator = QueueSimulator(random_seed=i)
            result = simulator.simulate(scenario)
            results.append(result)
        
        return results
    
    def _aggregate_results(self, scenario: ScenarioConfig, 
                          results: List[SimulationResults]) -> MonteCarloResults:
        """Aggregate individual simulation results with statistical analysis.
        
        Args:
            scenario: Original scenario configuration
            results: List of individual simulation results
            
        Returns:
            Aggregated Monte Carlo results with confidence intervals
        """
        if not results:
            raise ValueError("No simulation results to aggregate")
        
        # Extract metrics from all runs
        metrics = {
            'avg_wait_time': [r.avg_wait_time for r in results],
            'max_wait_time': [r.max_wait_time for r in results],
            'p95_wait_time': [r.p95_wait_time for r in results],
            'avg_queue_length': [r.avg_queue_length for r in results],
            'desk_utilization': [r.desk_utilization for r in results],
            'service_level_5min': [r.service_level_5min for r in results],
            'total_customers': [r.total_customers for r in results]
        }
        
        # Calculate means
        means = {key: np.mean(values) for key, values in metrics.items()}
        
        # Calculate 95% confidence intervals
        confidence_intervals = {}
        for key, values in metrics.items():
            if len(values) > 1:
                ci = self._calculate_confidence_interval(values, confidence_level=0.95)
                confidence_intervals[f"{key}_ci"] = ci
            else:
                # Single simulation - no confidence interval
                confidence_intervals[f"{key}_ci"] = (means[key], means[key])
        
        return MonteCarloResults(
            scenario_name=scenario.name,
            num_simulations=len(results),
            
            # Mean values
            avg_wait_time=means['avg_wait_time'],
            max_wait_time=means['max_wait_time'],
            p95_wait_time=means['p95_wait_time'],
            avg_queue_length=means['avg_queue_length'],
            desk_utilization=means['desk_utilization'],
            service_level_5min=means['service_level_5min'],
            
            # Confidence intervals
            avg_wait_time_ci=confidence_intervals['avg_wait_time_ci'],
            max_wait_time_ci=confidence_intervals['max_wait_time_ci'],
            p95_wait_time_ci=confidence_intervals['p95_wait_time_ci'],
            avg_queue_length_ci=confidence_intervals['avg_queue_length_ci'],
            desk_utilization_ci=confidence_intervals['desk_utilization_ci'],
            service_level_5min_ci=confidence_intervals['service_level_5min_ci'],
            
            # Additional statistics
            total_customers_mean=means['total_customers'],
            total_customers_std=np.std(metrics['total_customers'])
        )
    
    def _calculate_confidence_interval(self, values: List[float], 
                                     confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for a list of values.
        
        Args:
            values: List of numeric values
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        values_array = np.array(values)
        mean = np.mean(values_array)
        std_err = np.std(values_array, ddof=1) / np.sqrt(len(values_array))
        
        # Use t-distribution for small samples
        from scipy import stats
        degrees_freedom = len(values_array) - 1
        alpha = 1 - confidence_level
        t_critical = stats.t.ppf(1 - alpha/2, degrees_freedom)
        
        margin_error = t_critical * std_err
        
        return (mean - margin_error, mean + margin_error)
    
    def compare_scenarios(self, scenarios: List[ScenarioConfig]) -> Dict[str, MonteCarloResults]:
        """Run and compare multiple scenarios.
        
        Args:
            scenarios: List of scenario configurations to compare
            
        Returns:
            Dictionary mapping scenario names to their results
        """
        results = {}
        
        for scenario in scenarios:
            print(f"Running scenario: {scenario.name}")
            result = self.run_simulation(scenario)
            results[scenario.name] = result
        
        return results
    
    def generate_report(self, results: MonteCarloResults) -> str:
        """Generate a text report for Monte Carlo results.
        
        Args:
            results: Monte Carlo simulation results
            
        Returns:
            Formatted text report
        """
        report = f"""
Monte Carlo Simulation Report
=============================

Scenario: {results.scenario_name}
Number of simulations: {results.num_simulations}

Key Metrics (95% Confidence Intervals):
--------------------------------------
Average Wait Time: {results.avg_wait_time:.2f} minutes ({results.avg_wait_time_ci[0]:.2f} - {results.avg_wait_time_ci[1]:.2f})
95th Percentile Wait Time: {results.p95_wait_time:.2f} minutes ({results.p95_wait_time_ci[0]:.2f} - {results.p95_wait_time_ci[1]:.2f})
Maximum Wait Time: {results.max_wait_time:.2f} minutes ({results.max_wait_time_ci[0]:.2f} - {results.max_wait_time_ci[1]:.2f})
Average Queue Length: {results.avg_queue_length:.2f} customers ({results.avg_queue_length_ci[0]:.2f} - {results.avg_queue_length_ci[1]:.2f})
Desk Utilization: {results.desk_utilization:.1%} ({results.desk_utilization_ci[0]:.1%} - {results.desk_utilization_ci[1]:.1%})
Service Level (≤5 min): {results.service_level_5min:.1%} ({results.service_level_5min_ci[0]:.1%} - {results.service_level_5min_ci[1]:.1%})

Customer Statistics:
-------------------
Average Customers per Day: {results.total_customers_mean:.1f} ± {results.total_customers_std:.1f}
"""
        return report
