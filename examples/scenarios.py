"""
Example scenarios for the Click & Collect Queue Simulation System.
"""
from src.models import ScenarioConfig

# Basic weekday scenario with constant staffing for a large store
WEEKDAY_BASIC_LARGE = ScenarioConfig(
    name="Weekday Basic - 3 Desks",
    arrival_rates={
        10: 6,  # 10-11am: 6 customers/hour
        11: 8,  # 11-12pm: 8 customers/hour
        12: 10,  # 12-1pm: 10 customers/hour (lunch peak)
        13: 13,  # 1-2pm: 13 customers/hour
        14: 15,  # 2-3pm: 15 customers/hour
        15: 12,  # 3-4pm: 12 customers/hour
        16: 12,   # 4-5pm: 12 customers/hour
        17: 19,   # 5-6pm: 19 customers/hour
        18: 20,   # 6-7pm: 20 customers/hour
        19: 21,   # 7-8pm: 21 customers/hour
        20: 15,    # 8-9pm: 22 customers/hour
        21: 5,   # 9-10pm: 10 customers/hour    
    },
    num_desks=3,
    mean_service_time=3.0,  # 8.5 minutes average service time
    operating_hours=(10, 22),  # 10am to 10pm
    num_simulations=1000
)

# Basic weekday scenario with constant staffing for a small store
WEEKDAY_BASIC_SMALL = ScenarioConfig(
    name="Weekday Basic - 2 Desks",
    arrival_rates={
        10: 6,  # 10-11am: 6 customers/hour
        11: 9,  # 11-12pm: 8 customers/hour
        12: 10,  # 12-1pm: 10 customers/hour (lunch peak)
        13: 9,  # 1-2pm: 13 customers/hour
        14: 7,  # 2-3pm: 15 customers/hour
        15: 5,  # 3-4pm: 12 customers/hour
        16: 8,   # 4-5pm: 12 customers/hour
        17: 15,   # 5-6pm: 19 customers/hour
        18: 16,   # 6-7pm: 20 customers/hour
        19: 16,   # 7-8pm: 21 customers/hour
        20: 11,    # 8-9pm: 22 customers/hour
        21: 4,   # 9-10pm: 10 customers/hour    
    },
    num_desks=2,
    mean_service_time=3.0,  # 8.5 minutes average service time
    operating_hours=(10, 22),  # 10am to 10pm
    num_simulations=1000
)

# Peak season scenario with variable staffing
PEAKSEASON_DAY_VARIABLE = ScenarioConfig(
    name="Peak Day - Variable Staffing",
    arrival_rates={
        10: 28,  # 10-11am: 28 customers/hour
        11: 40,  # 11-12pm: 40 customers/hour
        12: 52,  # 12-1pm: 52 customers/hour (lunch peak)
        13: 63,  # 1-2pm: 63 customers/hour
        14: 74,  # 2-3pm: 74 customers/hour
        15: 61,  # 3-4pm: 12 customers/hour
        16: 62,   # 4-5pm: 62 customers/hour
        17: 93,   # 5-6pm: 93 customers/hour
        18: 100,   # 6-7pm: 100 customers/hour
        19: 104,   # 7-8pm: 104 customers/hour
        20: 75,    # 8-9pm: 75 customers/hour
        21: 26,   # 9-10pm: 26 customers/hour
    },
    desk_schedule={
        10: 4,  # Increase to 3 desks
        11: 4,  # Peak staffing for lunch rush
        12: 4,  # Maximum staffing
        13: 4,  # Reduce slightly
        14: 5,  # Back to normal
        15: 5,  # Reduced afternoon staffing
        16: 5,
        17: 6,   # Minimal evening staffing
        18: 6,
        19: 6,
        20: 6,
        21: 6
    },
    mean_service_time=3.0,  # Faster service time
    operating_hours=(10, 22),
    num_simulations=1000
)

# Weekend scenario Large Store - different pattern
WEEKEND_SCENARIO = ScenarioConfig(
    name="Weekend - Steady Flow",
    arrival_rates={
        10: 8,   # Later start on weekends
        11: 11,
        12: 13,
        13: 14,  # Weekend lunch peak
        14: 8,  # Afternoon shopping peak
        15: 7,
        16: 8,
        17: 11,
        18: 14,
        19: 17,
        20: 11,
        21: 6    # Extended hours
    },
    num_desks=3,
    mean_service_time= 3.0,  # Slightly longer service time
    operating_hours=(10, 22),  # 10am to 10pm
    num_simulations=1000
)


# Low service time scenario (efficient service) for Large Store
EFFICIENT_ORDERS = ScenarioConfig(
    name="Efficient Service - 3 Desks",
    arrival_rates={
        10: 6,  # 10-11am: 6 customers/hour
        11: 8,  # 11-12pm: 8 customers/hour
        12: 10,  # 12-1pm: 10 customers/hour (lunch peak)
        13: 13,  # 1-2pm: 13 customers/hour
        14: 15,  # 2-3pm: 15 customers/hour
        15: 12,  # 3-4pm: 12 customers/hour
        16: 12,   # 4-5pm: 12 customers/hour
        17: 19,   # 5-6pm: 19 customers/hour
        18: 20,   # 6-7pm: 20 customers/hour
        19: 21,   # 7-8pm: 21 customers/hour
        20: 15,    # 8-9pm: 22 customers/hour
        21: 5,   # 9-10pm: 10 customers/hour    
    },
    num_desks=3,
    mean_service_time=2.0,  # 2.0 minutes average service time
    operating_hours=(10, 22),  # 10am to 10pm
    num_simulations=1000
)

# All example scenarios
ALL_SCENARIOS = [
    WEEKDAY_BASIC_LARGE,
    WEEKDAY_BASIC_SMALL,
    PEAKSEASON_DAY_VARIABLE,
    WEEKEND_SCENARIO,
    EFFICIENT_ORDERS,
    # Additional scenarios can be added here
]
