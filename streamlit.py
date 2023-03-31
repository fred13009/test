import streamlit as st
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpStatus, LpConstraint
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

if "next_step" in st.session_state and st.session_state.next_step:
    st.markdown("---")
    st.header("How many channels do you want to cover?")
    st.session_state.num_channels = st.number_input("Number of channels:", min_value=2, max_value=10, value=2, step=1, format="%d")

    if st.button("Next Step Channels"):
        st.session_state.next_step_channels = True

if "next_step_channels" in st.session_state and st.session_state.next_step_channels:
    st.markdown("---")
    st.header("Marketing Channels")

    channels = []
    for i in range(1, st.session_state.num_channels + 1):
        channel = channel_input_form(i)
        channels.append(channel)

    if st.button("Run Calculations"):
        # Budget optimization part
        prob = LpProblem("Advertising Budget Allocation", LpMaximize)

        # Initialize variables
        allocation_vars = [LpVariable(f"allocation_{i}", lowBound=0) for i in range(st.session_state.num_channels)]
        revenue_vars = [LpVariable(f"revenue_{i}", lowBound=0) for i in range(st.session_state.num_channels)]

        # Objective function
        prob += lpSum(revenue_vars)

        # Constraints
        prob += lpSum(allocation_vars) <= st.session_state.overall_budget

        for i, channel in enumerate(channels):
            prob += allocation_vars[i] <= channel['max_budget'] if channel['max_budget'] is not None else 1e9
            prob += allocation_vars[i] >= channel['min_budget'] if channel['min_budget'] is not None else 0
            prob += revenue_vars[i] >= channel['min_revenue'] if channel['min_revenue'] is not None else 0
            prob += revenue_vars[i] <= allocation_vars[i] * channel['roas']

        if st.session_state.channel_exposure_constraint:
            prob += lpSum([LpConstraint(var, cat='Binary') for var in allocation_vars]) >= st.session_state.channel_exposure_constraint

        # Solve the optimization problem
        prob.solve()

        # Show results
        st.markdown("---")
        st.header("Optimal Budget Allocation")
        if LpStatus[prob.status] == 'Optimal':
            allocation_df = pd.DataFrame(columns=['Channel', 'Budget Allocation', 'Revenue'])
            for i, channel in enumerate(channels):
                allocation = allocation_vars[i].value()
                revenue = revenue_vars[i].value()
                allocation_df = allocation_df.append({'Channel': channel['name'], 'Budget Allocation': allocation, 'Revenue': revenue}, ignore_index=True)

            st.write(allocation_df)
        else:
            st.error("Optimization failed. Please check your constraints and try again.")
