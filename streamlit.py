import streamlit as st
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus
import pandas as pd

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

# Start of the second part
if "next_step" in st.session_state and st.session_state.next_step:
    st.markdown("---")
    st.header("How many channels do you want to cover?")
    st.session_state.num_channels = st.number_input("Number of channels:", min_value=2, max_value=10, value=2, step=1, format="%d")

    if st.button("Next Step Channels"):
        st.session_state.next_step_channels = True

# Channel data input
if "next_step_channels" in st.session_state and st.session_state.next_step_channels:
    st.markdown("---")
    st.header("Marketing Channels")

    channel_data = {}
    for i in range(1, st.session_state.num_channels + 1):
        channel_name = st.text_input(f"Channel {i} Name:", key=f"channel_{i}_name")
        historical_roas = st.number_input(f"Channel {i} Historical ROAS:", min_value=0.0, value=1.0, step=0.1, format="%.1f", key=f"channel_{i}_roas")

        channel_data[channel_name] = {"roas": historical_roas}

    st.session_state.channels = channel_data

    # Marketing Channel Constraints
    st.markdown("---")
    st.header("Marketing Channel Constraints")

    if use_channel_exposure_constraint:
        st.write(f"Minimum number of channels to use: {channel_exposure_constraint}")

    # Set a new constraint
    if st.button("Set New Constraint"):
        st.session_state.setting_constraint = True

    if "setting_constraint" in st.session_state and st.session_state.setting_constraint:
        channel_dropdown = st.selectbox("Select channel:", options=list(channel_data.keys()))
        constraint_dropdown = st.selectbox("Select constraint type:", options=["Minimum Budget", "Maximum Budget", "Minimum Revenue"])
        constraint_value = st.number_input("Enter constraint value:", min_value=0, value=0, step=1, format="%d")

        if channel_dropdown not in st.session_state.channels:
            st.session_state.channels[channel_dropdown] = {}

        constraint_key = constraint_dropdown.lower().replace(" ", "_")
        st.session_state.channels[channel_dropdown][constraint_key] = constraint_value

        if st.button("Save Constraint"):
            st.session_state.setting_constraint = False

# Run calculation
if st.button("Run Calculation"):
    # Budget optimization part

    # Create the problem
    prob = LpProblem("Budget_Allocation", LpMaximize)

    # Create decision variables
    allocation_vars = {
        channel: LpVariable(f"alloc_{channel}", lowBound=0, cat="Continuous") for channel in st.session_state.channels
    }

    # Objective function
    prob += lpSum([st.session_state.channels[channel]['roas'] * allocation_vars[channel] for channel in st.session_state.channels])

    # Budget constraint
    prob += lpSum([allocation_vars[channel] for channel in st.session_state.channels]) <= st.session_state.overall_budget

    # Channel exposure constraint
    if st.session_state.channel_exposure_constraint:
        prob += lpSum([allocation_vars[channel] >= 0.0001 for channel in st.session_state.channels]) >= st.session_state.channel_exposure_constraint

    # Individual channel constraints
    for channel in st.session_state.channels:
        if 'minimum_budget' in st.session_state.channels[channel]:
            prob += allocation_vars[channel] >= st.session_state.channels[channel]['minimum_budget']
        if 'maximum_budget' in st.session_state.channels[channel]:
            prob += allocation_vars[channel] <= st.session_state.channels[channel]['maximum_budget']
        if 'minimum_revenue' in st.session_state.channels[channel]:
            prob += st.session_state.channels[channel]['roas'] * allocation_vars[channel] >= st.session_state.channels[channel]['minimum_revenue']

    # Solve the problem
    prob.solve()

    # Check the status
    if LpStatus[prob.status] == "Optimal":
        # Display the results
        st.markdown("---")
        st.header("Optimal Budget Allocation")
        allocated_budget = {
            channel: allocation_vars[channel].varValue for channel in st.session_state.channels
        }
        allocated_revenue = {
            channel: st.session_state.channels[channel]['roas'] * allocation_vars[channel].varValue for channel in st.session_state.channels
        }

        # Dataframe for the results
        results_df = pd.DataFrame(
            {
                "Channel": list(st.session_state.channels.keys()),
                "Allocated Budget": list(allocated_budget.values()),
                "Estimated Revenue": list(allocated_revenue.values())
            }
        )

        st.write(results_df)
    else:
        st.warning("There is no optimal solution. Please check your constraints.")
