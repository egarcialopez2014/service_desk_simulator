#!/usr/bin/env python3
"""
Quick terminal runner for all scenarios in the Click & Collect Queue Simulation System.
"""
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.monte_carlo import MonteCarloRunner
from examples.scenarios import ALL_SCENARIOS


def run_all_scenarios():
    """Run all available scenarios and display results."""
    print("Click & Collect Queue Simulation System")
    print("=" * 60)
    print(f"Running {len(ALL_SCENARIOS)} scenarios...")
    print()
    
    runner = MonteCarloRunner()
    results = []
    
    for i, scenario in enumerate(ALL_SCENARIOS, 1):
        print(f"[{i}/{len(ALL_SCENARIOS)}] Running: {scenario.name}")
        print("-" * 40)
        
        try:
            # Run with fewer simulations for faster results
            scenario.num_simulations = 1000
            result = runner.run_simulation(scenario, parallel=False)
            results.append(result)
            
            # Display key metrics
            print(f"✅ Average Wait Time: {result.avg_wait_time:.2f} minutes")
            print(f"✅ Maximum Wait Time: {result.max_wait_time:.2f} minutes")
            print(f"✅ Service Level (≤5min): {result.service_level_5min:.1%}")
            print(f"✅ Desk Utilization: {result.desk_utilization:.1%}")
            print(f"✅ Expected Daily Customers: {result.total_customers_mean:.0f}")
            print(f"✅ Actual Customers Generated: {result.total_customers_mean:.0f} ± {result.total_customers_std:.0f}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    # Summary comparison
    if results:
        print("SCENARIO COMPARISON SUMMARY")
        print("=" * 110)
        print(f"{'Scenario':<25} {'Avg Wait':<10} {'Max Wait':<10} {'Service Level':<14} {'Utilization':<12} {'Customers':<12}")
        print("-" * 110)
        
        for result in results:
            name = result.scenario_name[:24]  # Truncate long names
            print(f"{name:<25} {result.avg_wait_time:>6.2f} min {result.max_wait_time:>6.2f} min {result.service_level_5min:>10.1%} {result.desk_utilization:>10.1%} {result.total_customers_mean:>8.0f}")


def run_single_scenario(scenario_name=None):
    """Run a single scenario by name."""
    if scenario_name is None:
        print("Available scenarios:")
        for i, scenario in enumerate(ALL_SCENARIOS, 1):
            print(f"  {i}. {scenario.name}")
        
        try:
            choice = int(input(f"\nSelect scenario (1-{len(ALL_SCENARIOS)}): "))
            if 1 <= choice <= len(ALL_SCENARIOS):
                selected_scenario = ALL_SCENARIOS[choice - 1]
            else:
                print("Invalid choice!")
                return
        except (ValueError, KeyboardInterrupt):
            print("Cancelled.")
            return
    else:
        # Find scenario by name
        selected_scenario = None
        for scenario in ALL_SCENARIOS:
            if scenario_name.lower() in scenario.name.lower():
                selected_scenario = scenario
                break
        
        if not selected_scenario:
            print(f"Scenario '{scenario_name}' not found!")
            return
    
    print(f"\nRunning scenario: {selected_scenario.name}")
    print("=" * 50)
    
    runner = MonteCarloRunner()
    
    try:
        # Run with full simulations for detailed results
        result = runner.run_simulation(selected_scenario)
        
        # Display detailed report
        print(runner.generate_report(result))
        
    except Exception as e:
        print(f"Error running simulation: {e}")


def main():
    """Main function with command line options."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            run_all_scenarios()
        elif command == "list":
            print("Available scenarios:")
            for i, scenario in enumerate(ALL_SCENARIOS, 1):
                print(f"  {i}. {scenario.name}")
                print(f"     Operating: {scenario.operating_hours[0]}:00-{scenario.operating_hours[1]}:00")
                print(f"     Service time: {scenario.mean_service_time} min")
                if scenario.num_desks:
                    print(f"     Desks: {scenario.num_desks} (constant)")
                else:
                    print(f"     Desks: Variable")
                print()
        elif command in ["help", "-h", "--help"]:
            print("Usage:")
            print("  python run_scenarios.py all       - Run all scenarios")
            print("  python run_scenarios.py list      - List available scenarios")
            print("  python run_scenarios.py           - Interactive single scenario")
            print("  python run_scenarios.py <name>    - Run scenario by name")
        else:
            # Try to run scenario by name
            run_single_scenario(command)
    else:
        # Interactive mode
        run_single_scenario()


if __name__ == "__main__":
    main()
