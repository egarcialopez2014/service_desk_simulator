"""
Streamlit web application for the Click & Collect Queue Simulation System.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import ScenarioConfig
from src.simulation.monte_carlo import MonteCarloRunner

# Force reload of scenarios module to pick up changes
import importlib
if 'examples.scenarios' in sys.modules:
    importlib.reload(sys.modules['examples.scenarios'])
from examples.scenarios import ALL_SCENARIOS


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Click & Collect Queue Simulator",
        page_icon="🛒",
        layout="wide"
    )
    
    st.title("🛒 Click & Collect Queue Simulation System")
    st.markdown("""
    Optimize your retail click & collect desk staffing using Monte Carlo simulation.
    Predict waiting times and analyze different staffing scenarios.
    """)
    
    # Sidebar for scenario selection and parameters
    st.sidebar.header("Simulation Parameters")
    
    # Choose between predefined scenarios or custom
    scenario_type = st.sidebar.radio(
        "Scenario Type",
        ["Predefined Scenarios", "Custom Scenario"]
    )
    
    if scenario_type == "Predefined Scenarios":
        scenario = create_predefined_scenario_ui()
    else:
        scenario = create_custom_scenario_ui()
    
    if scenario is None:
        st.warning("Please configure a scenario to run the simulation.")
        return
    
    # Simulation controls
    st.sidebar.header("Simulation Settings")
    num_simulations = st.sidebar.slider(
        "Number of Simulations", 
        min_value=10, 
        max_value=2000, 
        value=500,
        help="More simulations provide better statistical confidence but take longer to run."
    )
    
    # Update scenario with selected number of simulations
    scenario.num_simulations = num_simulations
    
    # Run simulation button
    if st.sidebar.button("🚀 Run Simulation", type="primary"):
        run_simulation(scenario)


def create_predefined_scenario_ui():
    """Create UI for selecting predefined scenarios."""
    scenario_names = [s.name for s in ALL_SCENARIOS]
    selected_name = st.sidebar.selectbox("Select Scenario", scenario_names)
    
    # Find the selected scenario
    selected_scenario = None
    for scenario in ALL_SCENARIOS:
        if scenario.name == selected_name:
            selected_scenario = scenario
            break
    
    if selected_scenario:
        # Display scenario details
        st.subheader(f"Scenario: {selected_scenario.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Mean Service Time", f"{selected_scenario.mean_service_time} min")
            st.metric("Operating Hours", f"{selected_scenario.operating_hours[0]}:00 - {selected_scenario.operating_hours[1]}:00")
            
        with col2:
            if selected_scenario.num_desks:
                st.metric("Desk Staffing", f"{selected_scenario.num_desks} desks (constant)")
            else:
                st.metric("Desk Staffing", "Variable (see schedule)")
        
        # Show arrival pattern
        display_arrival_pattern(selected_scenario)
        
        # Show desk schedule if variable
        if selected_scenario.desk_schedule:
            display_desk_schedule(selected_scenario)
    
    return selected_scenario


def create_custom_scenario_ui():
    """Create UI for building custom scenarios."""
    st.subheader("Custom Scenario Configuration")
    
    # Option to start from a template
    use_template = st.sidebar.checkbox("Start from existing scenario template", value=False)
    
    template_scenario = None
    if use_template:
        template_names = ["None"] + [s.name for s in ALL_SCENARIOS]
        selected_template = st.sidebar.selectbox("Select Template", template_names)
        
        if selected_template != "None":
            template_scenario = next((s for s in ALL_SCENARIOS if s.name == selected_template), None)
            if template_scenario:
                st.sidebar.success(f"✅ Template loaded: {selected_template}")
                st.sidebar.write("💡 All fields below are pre-filled. Modify as needed.")
    
    # Pre-populate values from template or use defaults
    default_name = template_scenario.name + " (Custom)" if template_scenario else "My Custom Scenario"
    default_start = template_scenario.operating_hours[0] if template_scenario else 9
    default_end = template_scenario.operating_hours[1] if template_scenario else 18
    default_service_time = template_scenario.mean_service_time if template_scenario else 8.5
    default_num_desks = template_scenario.num_desks if template_scenario and template_scenario.num_desks else 3
    default_staffing_type = "Variable" if template_scenario and template_scenario.desk_schedule else "Constant"
    
    scenario_name = st.sidebar.text_input("Scenario Name", default_name)
    
    # Operating hours
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_hour = st.selectbox("Start Hour", range(0, 24), index=default_start)
    with col2:
        end_hour = st.selectbox("End Hour", range(1, 25), index=default_end)
    
    if start_hour >= end_hour:
        st.sidebar.error("End hour must be after start hour")
        return None
    
    # Service time
    mean_service_time = st.sidebar.slider(
        "Mean Service Time (minutes)", 
        min_value=0.5, 
        max_value=5.0, 
        value=min(float(default_service_time), 5.0),  # Cap default at 5.0
        step=0.1
    )
    
    # Staffing configuration
    staffing_type = st.sidebar.radio("Staffing Type", ["Constant", "Variable"], 
                                   index=0 if default_staffing_type == "Constant" else 1)
    
    if staffing_type == "Constant":
        num_desks = st.sidebar.slider("Number of Desks", min_value=1, max_value=10, value=default_num_desks)
        desk_schedule = None
    else:
        st.sidebar.write("Configure desk schedule by hour:")
        desk_schedule = {}
        for hour in range(start_hour, end_hour):
            # Default desk count from template or use 3
            default_desk_count = 3
            if template_scenario and template_scenario.desk_schedule and hour in template_scenario.desk_schedule:
                default_desk_count = template_scenario.desk_schedule[hour]
            
            desks = st.sidebar.slider(
                f"{hour}:00-{hour+1}:00", 
                min_value=1, 
                max_value=10, 
                value=default_desk_count,
                key=f"desk_{hour}"
            )
            desk_schedule[hour] = desks
        num_desks = None
    
    # Arrival rates configuration
    st.write("### Arrival Rates Configuration")
    if template_scenario:
        # Show template info in an info box
        st.info(f"� **Template:** {template_scenario.name}\n\n"
                f"• **Operating Hours:** {template_scenario.operating_hours[0]}:00 - {template_scenario.operating_hours[1]}:00\n"
                f"• **Service Time:** {template_scenario.mean_service_time} min\n"
                f"• **Staffing:** {'Constant (' + str(template_scenario.num_desks) + ' desks)' if template_scenario.num_desks else 'Variable'}\n"
                f"• **Daily Customers:** ~{sum(template_scenario.arrival_rates.values())} customers/day")
        st.write("**Modify the values below as needed:**")
    else:
        st.write("Configure expected customer arrivals per hour:")
    
    arrival_rates = {}
    cols = st.columns(min(4, end_hour - start_hour))
    
    for i, hour in enumerate(range(start_hour, end_hour)):
        col_idx = i % len(cols)
        with cols[col_idx]:
            # Default arrival rate from template or use 10
            default_rate = 10.0
            if template_scenario and hour in template_scenario.arrival_rates:
                default_rate = float(template_scenario.arrival_rates[hour])
            
            rate = st.number_input(
                f"{hour}:00-{hour+1}:00",
                min_value=0.0,
                max_value=200.0,
                value=default_rate,
                step=1.0,
                key=f"arrival_{hour}"
            )
            arrival_rates[hour] = rate
    
    # Create scenario
    try:
        scenario = ScenarioConfig(
            name=scenario_name,
            arrival_rates=arrival_rates,
            num_desks=num_desks,
            desk_schedule=desk_schedule,
            mean_service_time=mean_service_time,
            operating_hours=(start_hour, end_hour),
            num_simulations=500  # Default, will be updated
        )
        
        # Display the configured scenario
        display_arrival_pattern(scenario)
        if scenario.desk_schedule:
            display_desk_schedule(scenario)
        
        return scenario
        
    except Exception as e:
        st.error(f"Invalid scenario configuration: {e}")
        return None


def display_arrival_pattern(scenario):
    """Display the arrival pattern chart."""
    st.write("### Customer Arrival Pattern")
    
    hours = list(scenario.arrival_rates.keys())
    rates = list(scenario.arrival_rates.values())
    
    fig = px.bar(
        x=hours, 
        y=rates,
        labels={'x': 'Hour of Day', 'y': 'Customers per Hour'},
        title="Expected Customer Arrivals by Hour"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def display_desk_schedule(scenario):
    """Display the desk staffing schedule."""
    st.write("### Desk Staffing Schedule")
    
    hours = list(scenario.desk_schedule.keys())
    desks = list(scenario.desk_schedule.values())
    
    fig = px.line(
        x=hours, 
        y=desks,
        labels={'x': 'Hour of Day', 'y': 'Number of Desks'},
        title="Desk Staffing by Hour",
        markers=True
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def run_simulation(scenario):
    """Run the Monte Carlo simulation and display results."""
    st.header("🔄 Running Simulation...")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize runner
        runner = MonteCarloRunner()
        
        # Update progress
        progress_bar.progress(0.2)
        status_text.text("Initializing simulation...")
        
        # Run simulation
        progress_bar.progress(0.5)
        status_text.text("Running Monte Carlo simulation...")
        
        results = runner.run_simulation(scenario)
        
        progress_bar.progress(1.0)
        status_text.text("Simulation complete!")
        
        # Display results
        display_results(results)
        
    except Exception as e:
        st.error(f"Simulation failed: {e}")
        st.write("Please check your scenario configuration and try again.")


def display_results(results):
    """Display simulation results."""
    st.header("📊 Simulation Results")
    
    # Key metrics - using 5 columns now to include 95th percentile
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Average Wait Time",
            f"{results.avg_wait_time:.2f} min",
            help="Average time customers wait before being served"
        )
    
    with col2:
        st.metric(
            "95th Percentile Wait",
            f"{results.p95_wait_time:.2f} min",
            help="95% of customers wait less than this time"
        )
    
    with col3:
        st.metric(
            "Maximum Wait Time",
            f"{results.max_wait_time:.2f} min",
            help="Longest wait time experienced by any customer"
        )
    
    with col4:
        st.metric(
            "Service Level (≤5 min)",
            f"{results.service_level_5min:.1%}",
            help="Percentage of customers served within 5 minutes"
        )
    
    with col5:
        st.metric(
            "Desk Utilization",
            f"{results.desk_utilization:.1%}",
            help="Average percentage of time desks are busy"
        )
    
    # Detailed results with confidence intervals
    st.subheader("Detailed Results (95% Confidence Intervals)")
    
    metrics_data = {
        "Metric": [
            "Average Wait Time (min)",
            "95th Percentile Wait Time (min)",
            "Maximum Wait Time (min)",
            "Average Queue Length",
            "Desk Utilization (%)",
            "Service Level ≤5min (%)"
        ],
        "Value": [
            f"{results.avg_wait_time:.2f}",
            f"{results.p95_wait_time:.2f}",
            f"{results.max_wait_time:.2f}",
            f"{results.avg_queue_length:.2f}",
            f"{results.desk_utilization:.1%}",
            f"{results.service_level_5min:.1%}"
        ],
        "95% CI Lower": [
            f"{results.avg_wait_time_ci[0]:.2f}",
            f"{results.p95_wait_time_ci[0]:.2f}",
            f"{results.max_wait_time_ci[0]:.2f}",
            f"{results.avg_queue_length_ci[0]:.2f}",
            f"{results.desk_utilization_ci[0]:.1%}",
            f"{results.service_level_5min_ci[0]:.1%}"
        ],
        "95% CI Upper": [
            f"{results.avg_wait_time_ci[1]:.2f}",
            f"{results.p95_wait_time_ci[1]:.2f}",
            f"{results.max_wait_time_ci[1]:.2f}",
            f"{results.avg_queue_length_ci[1]:.2f}",
            f"{results.desk_utilization_ci[1]:.1%}",
            f"{results.service_level_5min_ci[1]:.1%}"
        ]
    }
    
    df = pd.DataFrame(metrics_data)
    st.dataframe(df, use_container_width=True)
    
    # Additional statistics
    st.subheader("Additional Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Number of Simulations:** {results.num_simulations}")
        st.write(f"**Average Customers per Day:** {results.total_customers_mean:.1f} ± {results.total_customers_std:.1f}")
    
    # Text report
    with st.expander("📄 Detailed Report"):
        runner = MonteCarloRunner()
        report = runner.generate_report(results)
        st.text(report)


if __name__ == "__main__":
    main()
