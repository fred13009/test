import streamlit as st
import pandas as pd
import pulp

def allocate_budget(channels, budget, min_channels):
    prob = pulp.LpProblem("BudgetAllocation", pulp.LpMaximize)

    alloc_vars = [pulp.LpVariable(f"alloc_{i}", lowBound=0) for i in range(len(channels))]

    prob += pulp.lpSum([c['ROAS'] * alloc for c, alloc in zip(channels, alloc_vars)])

    prob += pulp.lpSum(alloc_vars) <= budget

    for i, c in enumerate(channels):
        if c['min_budget']:
            prob += alloc_vars[i] >= c['min_budget']
        if c['max_budget']:
            prob += alloc_vars[i] <= c['max_budget']
        if c['min_revenue']:
            prob += c['ROAS'] * alloc_vars[i] >= c['min_revenue']

    if min_channels:
        prob += pulp.lpSum([pulp.LpVariable(f"binary_{i}", cat="Binary") for i in range(len(alloc_vars))]) >= min_channels

    prob.solve()

    if prob.status == 1:
        return [v.varValue for v in alloc_vars]
    else:
        return None

def main():
    st.title("Advertising Budget Allocation")
    budget = st.number_input("Overall budget", min_value=0, value=1000)

    use_min_channels = st.checkbox("Use minimum number of channels constraint?")
    if use_min_channels:
        min_channels = st.number_input("Minimum number of channels", min_value=1, value=1, key='min_channels')
    else:
        min_channels = 1

    st.subheader("Channel Information")
    n_channels = st.number_input("Number of channels", min_value=2, value=2)

    channels = []

    for i in range(n_channels):
        st.subheader(f"Channel {i + 1}")
        name = st.text_input("Name", value=f"Channel {i + 1}", key=f"name{i}")
        ROAS = st.number_input("Historical ROAS", min_value=0.0, value=1.0, key=f"ROAS{i}")
        min_budget = st.number_input("Minimum budget constraint (optional)", min_value=0, value=0, key=f"min_budget{i}")
        max_budget = st.number_input("Maximum budget constraint (optional)", min_value=0, value=0, key=f"max_budget{i}")
        min_revenue = st.number_input("Minimum revenue constraint (optional)", min_value=0, value=0, key=f"min_revenue{i}")

        channels.append({
            'name': name,
            'ROAS': ROAS,
            'min_budget': min_budget,
            'max_budget': max_budget,
            'min_revenue': min_revenue
        })

    if st.button("Submit for calculation"):
    allocation = allocate_budget(channels, budget, min_channels)

    if allocation is not None:
        st.subheader("Budget Allocation")
        for name, alloc in zip([c['name'] for c in channels], allocation):
            st.write(f"{name}: {alloc:.2f}")

        st.subheader("Overall Revenue")
        st.write(f"Expected: {sum([c['ROAS'] * alloc for c, alloc in zip(channels, allocation)]):.2f}")
        st.write(f"Even Split: {sum([c['ROAS'] * (budget / n_channels) for c in channels]):.2f}")
