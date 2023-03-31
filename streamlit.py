import streamlit as st
import pandas as pd
import pulp

st.title("Advertising Budget Allocation")
st.header("Step 1: Enter Overall Budget")

overall_budget = st.number_input("Overall Budget", min_value=0.0, step=0.01)

next_step1 = st.button("Next")

if next_step1:
    st.header("Step 2: Enter Number of Channels")
    
    num_channels = st.number_input("Number of Channels", min_value=2, step=1)
    
    next_step2 = st.button("Next", key="next_step2")

if next_step1 and next_step2:
    st.header("Step 3: Enter Channel Names and Historical ROAS")
    
    channel_data = {}
    
    for i in range(num_channels):
        col1, col2 = st.columns(2)
        
        with col1:
            channel_name = st.text_input(f"Channel {i+1} Name", key=f"channel_name_{i+1}")
        with col2:
            channel_roas = st.number_input(f"Channel {i+1} ROAS", min_value=0.0, step=0.01, value=1.1, key=f"channel_roas_{i+1}")
        
        channel_data[channel_name] = channel_roas
    
    next_step3 = st.button("Next", key="next_step3")

constraints = []

if next_step1 and next_step2 and next_step3:
    st.header("Step 4: Set Constraints")

    selected_channel = st.selectbox("Select Channel", options=list(channel_data.keys()))
    constraint_type = st.selectbox("Select Constraint Type", options=["Minimum Budget Constraint", "Maximum Budget Constraint", "Minimum Revenue Constraint"])

    constraint_value = st.number_input("Enter Constraint Value", min_value=0.0, step=0.01)

    add_constraint = st.button("Add Constraint")
    submit_calculation = st.button("Submit for Calculation")

    if add_constraint:
        constraints.append((selected_channel, constraint_type, constraint_value))
        st.write(f"Added {constraint_type} for {selected_channel}: {constraint_value}")

def allocate_budget(channel_data, constraints, overall_budget):
    prob = pulp.LpProblem("AdvertisingBudgetAllocation", pulp.LpMaximize)

    # Create budget allocation variables for each channel
    budget_vars = pulp.LpVariable.dicts("Budget", channel_data.keys(), lowBound=0, cat='Continuous')

    # Add constraints
    for channel, constraint_type, constraint_value in constraints:
        if constraint_type == "Minimum Budget Constraint":
            prob += budget_vars[channel] >= constraint_value
        elif constraint_type == "Maximum Budget Constraint":
            prob += budget_vars[channel] <= constraint_value
        elif constraint_type == "Minimum Revenue Constraint":
            prob += budget_vars[channel] * channel_data[channel] >= constraint_value

    # Add the overall budget constraint
    prob += pulp.lpSum([budget_vars[channel] for channel in channel_data.keys()]) <= overall_budget

    # Set the objective function to maximize overall revenue
    prob += pulp.lpSum([budget_vars[channel] * channel_data[channel] for channel in channel_data.keys()])

    # Solve the problem
    prob.solve()

    # Return the budget allocation and the expected revenue
    budget_allocation = {channel: budget_vars[channel].varValue for channel in channel_data.keys()}
    expected_revenue = pulp.value(prob.objective)

    return budget_allocation, expected_revenue

if next_step1 and next_step2 and next_step3 and submit_calculation:
    budget_allocation, expected_revenue = allocate_budget(channel_data, constraints, overall_budget)

    st.header("Optimized Budget Allocation")
    st.write(pd.DataFrame(budget_allocation.items(), columns=["Channel", "Budget Allocation"]))

    st.header("Expected Optimized Overall Revenue")
    st.write(expected_revenue)

    even_split_budget = overall_budget / num_channels
    even_split_revenue = sum([even_split_budget * channel_data[channel] for channel in channel_data.keys()])
    
    st.header("Revenue if Budget was Split Evenly Across Channels")
    st.write(even_split_revenue)
