import streamlit as st
import pulp

# Initialize Streamlit app
st.set_page_config(page_title="Advertising Budget Allocation", page_icon=None, layout="centered", initial_sidebar_state="expanded")

st.title("Advertising Budget Allocation")

# Input overall budget
overall_budget = st.number_input("Enter your overall budget:", min_value=0, value=1000, step=1, format="%d")
st.markdown("---")

# Input optional channel exposure constraint
use_channel_exposure_constraint = st.checkbox("Use channel exposure constraint")
channel_exposure_constraint = None
if use_channel_exposure_constraint:
    channel_exposure_constraint = st.number_input("Enter minimum number of channels to use:", min_value=2, max_value=10, value=2, step=1, format="%d")
    
# Next step button
if st.button("Next Step"):
    st.session_state.overall_budget = overall_budget
    st.session_state.channel_exposure_constraint = channel_exposure_constraint
    st.session_state.next_step = True

if "next_step" in st.session_state and st.session_state.next_step:
    st.markdown("---")
    st.header("How many channels do you want to cover?")
    st.session_state.num_channels = st.number_input("Number of channels:", min_value=2, max_value=10, value=2, step=1, format="%d")

    if st.button("Next Step Channels"):
        st.session_state.next_step_channels = True

def channel_input_form(channel_number):
    channel_name = st.text_input(f"Channel {channel_number} Name:", key=f"channel_{channel_number}_name")
    historical_roas = st.number_input(f"Channel {channel_number} Historical ROAS:", min_value=0.0, value=1.0, step=0.1, format="%.1f", key=f"channel_{channel_number}_roas")

    min_budget = st.number_input(f"Channel {channel_number} Minimum Budget (Optional):", min_value=0, value=0, step=1, format="%d", key=f"channel_{channel_number}_min_budget")
    max_budget = st.number_input(f"Channel {channel_number} Maximum Budget (Optional):", min_value=min_budget, value=1000, step=1, format="%d", key=f"channel_{channel_number}_max_budget")

    min_revenue = st.number_input(f"Channel {channel_number} Minimum Revenue (Optional):", min_value=0, value=0, step=1, format="%d", key=f"channel_{channel_number}_min_revenue")

    return {
        "name": channel_name,
        "roas": historical_roas,
        "min_budget": min_budget if min_budget > 0 else None,
        "max_budget": max_budget if max_budget > 0 else None,
        "min_revenue": min_revenue if min_revenue > 0 else None,
    }

if "next_step_channels" in st.session_state and st.session_state.next_step_channels:
    st.markdown("---")
    st.header("Marketing Channels")

    channels = []
    for i in range(1, st.session_state.num_channels + 1):
        channel = channel_input_form(i)
        channels.append(channel)

    # Next step to run the optimization
    if st.button("Run Optimization"):
        st.session_state.channels = channels
        st.session_state.run_optimization = True

# Budget optimization part

def optimize_budget_allocation(channels, overall_budget, channel_exposure_constraint):
    num_channels = len(channels)

    # Create the LP problem
    problem = pulp.LpProblem("Budget Allocation", pulp.LpMaximize)

    # Create variables
    budget_vars = pulp.LpVariable.dicts("Budget", [i for i in range(num_channels)], lowBound=0)
    exposure_vars = pulp.LpVariable.dicts("Exposure", [i for i in range(num_channels)], cat="Binary")

    # Set the objective function
    problem += pulp.lpSum([channels[i]["roas"] * budget_vars[i] for i in range(num_channels)])

    # Set the budget constraint
    problem += pulp.lpSum([budget_vars[i] for i in range(num_channels)]) <= overall_budget

    # Set the channel exposure constraint, if specified
    if channel_exposure_constraint:
        problem += pulp.lpSum([exposure_vars[i] for i in range(num_channels)]) >= channel_exposure_constraint

    # Set the individual channel constraints
    for i in range(num_channels):
        channel = channels[i]

        # Budget constraints
        if channel["min_budget"]:
            problem += budget_vars[i] >= channel["min_budget"] * exposure_vars[i]
        if channel["max_budget"]:
            problem += budget_vars[i] <= channel["max_budget"] * exposure_vars[i]

        # Revenue constraint
        if channel["min_revenue"]:
            problem += budget_vars[i] * channel["roas"] >= channel["min_revenue"] * exposure_vars[i]

    # Solve the problem
    problem.solve()

    # Get the optimized budget allocation
    optimized_allocation = [{"name": channels[i]["name"], "budget": budget_vars[i].value()} for i in range(num_channels)]

    return optimized_allocation

# Run the optimization
if "run_optimization" in st.session_state and st.session_state.run_optimization:
    optimized_allocation = optimize_budget_allocation(st.session_state.channels, st.session_state.overall_budget, st.session_state.channel_exposure_constraint)

    # Display the results
    st.markdown("---")
    st.header("Optimized Budget Allocation")

    for channel in optimized_allocation:
        st.write(f"{channel['name']}: ${channel['budget']:.2f}")
