import streamlit as st
import pandas as pd
import pulp

def _get_state():
    if 'state' not in st.session_state:
        st.session_state['state'] = {}
    return st.session_state['state']

def step1(state):
    st.header("Step 1: Enter Overall Budget")

    with st.form(key="step1_form"):
        overall_budget = st.number_input("Overall Budget", min_value=0.0, step=0.01)
        next_step1 = st.form_submit_button("Next")

    if next_step1:
        state['overall_budget'] = overall_budget
        state['step'] = 2

def step2(state):
    st.header("Step 2: Enter Number of Channels")

    with st.form(key="step2_form"):
        num_channels = st.number_input("Number of Channels", min_value=2, step=1)
        next_step2 = st.form_submit_button("Next")

    if next_step2:
        state['num_channels'] = num_channels
        state['step'] = 3
        state['channel_data'] = {i: {"name": "", "roas": 1.1} for i in range(1, num_channels + 1)}

def step3(state):
    st.header("Step 3: Enter Channel Names and Historical ROAS")

    num_channels = state['num_channels']
    channel_data = state['channel_data']

    with st.form(key="step3_form"):
        for i in range(1, num_channels + 1):
            col1, col2 = st.columns(2)
            with col1:
                channel_name = st.text_input(f"Channel {i} Name", key=f"channel_name_{i}")
            with col2:
                channel_roas = st.number_input(f"Channel {i} ROAS", min_value=0.0, step=0.01, value=1.1, key=f"channel_roas_{i}")

            channel_data[i]['name'] = channel_name
            channel_data[i]['roas'] = channel_roas

        next_step3 = st.form_submit_button("Next")

    if next_step3:
        state['step'] = 4
        state['channel_data'] = channel_data

def step4(state):
    st.header("Step 4: Set Constraints")

    channel_data = state['channel_data']
    channels = [channel_data[i]['name'] for i in channel_data]

    with st.form(key="step4_form"):
        selected_channel = st.selectbox("Select Channel", options=channels)
        constraint_type = st.selectbox("Select Constraint Type", options=["Minimum Budget Constraint", "Maximum Budget Constraint", "Minimum Revenue Constraint"])

        constraint_value = st.number_input("Enter Constraint Value", min_value=0.0, step=0.01)

        add_constraint = st.form_submit_button("Add Constraint")
        submit_calculation = st.form_submit_button("Submit for Calculation")

    if add_constraint:
        if 'constraints' not in state:
            state['constraints'] = []
        state['constraints'].append((selected_channel, constraint_type, constraint_value))
        st.write(f"Added {constraint_type} for {selected_channel}: {constraint_value}")

    if submit_calculation:
        state['step'] = 5

def step5(state):
    st.header("Optimized Budget Allocation")

    overall_budget = state['overall_budget']
    channel_data = {state['channel_data'][i]['name']: state['channel_data'][i]['roas'] for i in state['channel_data']}
    constraints = state['constraints']

    budget_allocation, expected_revenue = allocate_budget(channel_data, constraints, overall_budget)

    st.write(pd.DataFrame(budget_allocation.items(), columns=["Channel", "Budget Allocation"]))

    st.header("Expected Optimized Overall Revenue")
    st.write(expected_revenue)

    even_split_budget = overall_budget / len(channel_data)
    even_split_revenue = sum([even_split_budget * channel_data[channel] for channel in channel_data.keys()])

    st.header("Revenue if Budget was Split Evenly Across Channels")
    st.write(even_split_revenue)

def allocate_budget(channel_data, constraints, overall_budget):
    prob = pulp.LpProblem("AdvertisingBudgetAllocation", pulp.LpMaximize)

    budget_vars = pulp.LpVariable.dicts("Budget", channel_data.keys(), lowBound=0, cat='Continuous')

    for channel, constraint_type, constraint_value in constraints:
        if constraint_type == "Minimum Budget Constraint":
            prob += budget_vars[channel] >= constraint_value
        elif constraint_type == "Maximum Budget Constraint":
            prob += budget_vars[channel] <= constraint_value
        elif constraint_type == "Minimum Revenue Constraint":
            prob += budget_vars[channel] * channel_data[channel] >= constraint_value

    prob += pulp.lpSum([budget_vars[channel] for channel in channel_data.keys()]) <= overall_budget

    prob += pulp.lpSum([budget_vars[channel] * channel_data[channel] for channel in channel_data.keys()])

    prob.solve()

    budget_allocation = {channel: budget_vars[channel].varValue for channel in channel_data.keys()}
    expected_revenue = pulp.value(prob.objective)

    return budget_allocation, expected_revenue

st.title("Advertising Budget Allocation")

state = _get_state()

if 'step' not in state:
    state['step'] = 1

if state['step'] == 1:
    step1(state)
elif state['step'] == 2:
    step2(state)
elif state['step'] == 3:
    step3(state)
elif state['step'] == 4:
    step4(state)
elif state['step'] == 5:
    step5(state)
