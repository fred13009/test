import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus, LpConstraint

# Initialize Streamlit app
st.set_page_config(page_title="Advertising Budget Allocation", page_icon=None, layout="centered", initial_sidebar_state="expanded")

st.title("Advertising Budget Allocation")

# Input overall budget
overall_budget = st.number_input("Enter your overall budget:", min_value=0, value=1000, step=1, format="%d")
st.markdown("---")

# Next step button
if st.button("Next Step"):
    st.session_state.overall_budget = overall_budget
    st.session_state.next_step = True

# Start of the second part
def channel_input_form(channel_number):
    channel_name = st.text_input(f"Channel {channel_number} Name:", key=f"channel_{channel_number}_name")
    historical_roas = st.number_input(f"Channel {channel_number} Historical ROAS:", min_value=0.0, value=1.0, step=0.1, format="%.1f", key=f"channel_{channel_number}_roas")

    return {
        "name": channel_name,
        "roas": historical_roas,
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

    if st.button("Set Constraints"):
        st.session_state.channels = channels
        st.session_state.next_step_constraints = True

if "next_step_constraints" in st.session_state and st.session_state.next_step_constraints:
    st.markdown("---")
    st.header("Marketing Channel Constraints")

    channel_constraints = []
    for i, channel in enumerate(st.session_state.channels, start=1):
        min_budget = st.number_input(f"Channel {i} Minimum Budget (Optional):", min_value=0, value=0, step=1, format="%d", key=f"channel_{i}_min_budget")
        max_budget = st.number_input(f"Channel {i} Maximum Budget (Optional):", min_value=min_budget, value=1000, step=1, format="%d", key=f"channel_{i}_max_budget")
        min_revenue = st.number_input(f"Channel {i} Minimum Revenue (Optional):", min_value=0, value=0, step=1, format="%d", key=f"channel_{i}_min_revenue")

        channel_constraints.append({
            "min_budget": min_budget if min_budget > 0 else None,
            "max_budget": max_budget if max_budget > 0 else None,
            "min_revenue": min_revenue if min_revenue > 0 else None,
        })

    st.session_state.channel_constraints = channel_constraints
    st.markdown("---")

    if st.button("Run Calculations"):
        # Budget optimization part
        prob = LpProblem("Optimal_Budget_Allocation", LpMaximize)

        channel_vars = []
        for i, channel in enumerate(st.session_state.channels, start=1):
            channel_vars.append(LpVariable(f"Channel_{i}_Budget", 0, None))

        prob += lpSum([channel_vars[i] * st.session_state.channels[i]["roas"] for i in range(len(channel_vars))]), "Total Revenue"

        prob += lpSum(channel_vars) <= st.session_state.overall_budget, "Overall_Budget"

        for i, constraint in enumerate(st.session_state.channel_constraints, start=0):
            if constraint["min_budget"]:
                prob += channel_vars[i] >= constraint["min_budget"], f"Channel_{i + 1}_Min_Budget"
            if constraint["max_budget"]:
                prob += channel_vars[i] <= constraint["max_budget"], f"Channel_{i + 1}_Max_Budget"
            if constraint["min_revenue"]:
                prob += channel_vars[i] * st.session_state.channels[i]["roas"] >= constraint["min_revenue"], f"Channel_{i + 1}_Min_Revenue"

        prob.solve()

        if LpStatus[prob.status] == "Optimal":
            st.markdown("---")
            st.header("Optimal Budget Allocation")
            allocated_budgets = [var.value() for var in channel_vars]
            total_revenue = sum([allocated_budgets[i] * st.session_state.channels[i]["roas"] for i in range(len(allocated_budgets))])

            for i, channel in enumerate(st.session_state.channels, start=1):
                st.write(f"{channel['name']}: ${allocated_budgets[i - 1]:,.2f}")

            st.write(f"Total Revenue: ${total_revenue:,.2f}")

        else:
            st.warning("No optimal solution found. Please check your constraints and try again.")
