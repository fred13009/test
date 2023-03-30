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

    min_budget = st.number_input(f"Channel {channel_number} Minimum Budget (Optional):", min_value=0, value=None, step=1, format="%d", key=f"channel_{channel_number}_min_budget")
    max_budget = st.number_input(f"Channel {channel_number} Maximum Budget (Optional):", min_value=0, value=None, step=1, format="%d", key=f"channel_{channel_number}_max_budget")

    min_revenue = st.number_input(f"Channel {channel_number} Minimum Revenue (Optional):", min_value=0, value=None, step=1, format="%d", key=f"channel_{channel_number}_min_revenue")

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
if st.button("Run Calculation"):
    from pulp import LpProblem, LpMaximize, LpVariable, LpInteger, LpStatus, lpSum

    # Create the LP problem
    problem = LpProblem("BudgetAllocation", LpMaximize)

    # Create LP variables
    budget_vars = [LpVariable(f"Budget_Channel_{i}", lowBound=0, upBound=overall_budget, cat="Continuous") for i in range(len(channels))]
    exposure_vars = [LpVariable(f"Exposure_Channel_{i}", lowBound=0, upBound=1, cat="Integer") for i in range(len(channels))]

    # Objective function: maximize total revenue
    problem += lpSum([budget_vars[i] * channels[i]["roas"] for i in range(len(channels))])

    # Overall budget constraint
    problem += lpSum([budget_vars[i] for i in range(len(channels))]) <= overall_budget

    # Channel exposure constraint
    if channel_exposure_constraint:
        problem += lpSum([exposure_vars[i] for i in range(len(channels))]) >= channel_exposure_constraint

    # Channel-specific constraints
    for i, channel in enumerate(channels):
        # Budget constraints
        if channel["min_budget"]:
            problem += budget_vars[i] >= channel["min_budget"] * exposure_vars[i]
        if channel["max_budget"]:
            problem += budget_vars[i] <= channel["max_budget"] * exposure_vars[i]
        else:
            problem += budget_vars[i] <= overall_budget * exposure_vars[i]

        # Minimum revenue constraint
        if channel["min_revenue"]:
            problem += budget_vars[i] * channels[i]["roas"] >= channel["min_revenue"] * exposure_vars[i]

    # Solve the LP problem
    problem.solve()

    # Check the solution status
    if LpStatus[problem.status] == "Optimal":
        st.success("Optimal solution found.")
    else:
        st.error("No optimal solution found. Please review the constraints.")

    # Display the results
    st.markdown("---")
    st.header("Budget Allocation Results")
    for i, channel in enumerate(channels):
        st.write(f"{channel['name']}: ${budget_vars[i].varValue:.2f}")

    # Calculate the expected overall revenue
    expected_revenue = sum([budget_vars[i].varValue * channels[i]["roas"] for i in range(len(channels))])
    st.write(f"Expected Overall Revenue: ${expected_revenue:.2f}")

    # Compare with evenly split budget
    even_split_revenue = sum([(overall_budget / len(channels)) * channels[i]["roas"] for i in range(len(channels))])
    st.write(f"Revenue if Budget Was Split Evenly: ${even_split_revenue:.2f}")
