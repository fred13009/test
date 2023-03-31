import streamlit as st
import pandas as pd
import pulp

def main():
    st.title("Advertising Budget Allocation")
    state = st.session_state

    if "step" not in state:
        state.step = 1

    if state.step == 1:
        step1(state)
    elif state.step == 2:
        step2(state)
    elif state.step == 3:
        step3(state)
    elif state.step == 4:
        step4(state)

def step1(state):
    st.header("Step 1: Enter Overall Budget")
    state.overall_budget = st.number_input("Overall Budget", min_value=0.0, step=0.01)

    next_step1 = st.button("Next")
    if next_step1:
        state.step = 2

def step2(state):
    st.header("Step 2: Enter Number of Channels")
    num_channels = st.number_input("Number of Channels", min_value=2, step=1)

    next_step2 = st.button("Next")
    if next_step2:
        state.num_channels = num_channels
        state.step = 3
        state.channel_data = {}

def step3(state):
    st.header("Step 3: Enter Channel Names and Historical ROAS")

    for i in range(state.num_channels):
        col1, col2 = st.columns(2)

        with col1:
            channel_name = st.text_input(f"Channel {i+1} Name", key=f"channel_name_{i+1}")
        with col2:
            channel_roas = st.number_input(f"Channel {i+1} ROAS", min_value=0.0, step=0.01, value=1.1, key=f"channel_roas_{i+1}")

        state.channel_data[channel_name] = channel_roas

    next_step3 = st.button("Next")
    if next_step3:
        state.step = 4
        state.constraints = []

def step4(state):
    st.header("Step 4: Set Constraints")

    selected_channel = st.selectbox("Select Channel", options=list(state.channel_data.keys()))
    constraint_type = st.selectbox("Select Constraint Type", options=["Minimum Budget Constraint", "Maximum Budget Constraint", "Minimum Revenue Constraint"])

    constraint_value = st.number_input("Enter Constraint Value", min_value=0.0, step=0.01)

    add_constraint = st.button("Add Constraint")
    submit_calculation = st.button("Submit for Calculation")

    if add_constraint:
        state.constraints.append((selected_channel, constraint_type, constraint_value))
        st.write(f"Added {constraint_type} for {selected_channel}: {constraint_value}")

    if submit_calculation:
        budget_allocation, expected_revenue = allocate_budget(state.channel_data, state.constraints, state.overall_budget)

        st.header("Optimized Budget Allocation")
        st.write(pd.DataFrame(budget_allocation.items(), columns=["Channel", "Budget Allocation"]))

        st.header("Expected Optimized Overall Revenue")
        st.write(expected_revenue)

        even_split_budget = state.overall_budget / state.num_channels
        even_split_revenue = sum([even_split_budget * state.channel_data[channel] for channel in state.channel_data.keys()])

        st.header("Revenue if Budget was Split Evenly Across Channels")
        st.write(even_split_revenue)

if __name__ == "__main__":
    main()
