import streamlit as st
import pandas as pd
import pulp

def allocate_budget(channels, budget, min_channels):
    prob = pulp.LpProblem("BudgetAllocation", pulp.LpMaximize)

    x = [pulp.LpVariable(f'x{i}', channel['min_budget'] or 0, channel['max_budget']) for i, channel in enumerate(channels)]
    revenue = [channel['ROAS'] * x_i for channel, x_i in zip(channels, x)]

    # Objective function
    prob += pulp.lpSum(revenue)

    # Budget constraint
    prob += pulp.lpSum(x) <= budget, "TotalBudget"

    # Channel exposure constraint
    prob += pulp.lpSum([pulp.lpBinaryVar(f'y{i}') for i, channel in enumerate(channels)]) >= min_channels, "ChannelExposure"
    for i, channel in enumerate(channels):
        prob += x[i] - channel['min_budget'] * pulp.lpBinaryVar(f'y{i}') >= 0, f"MinBudget{i}"

    # Minimum revenue constraint
    for i, channel in enumerate(channels):
        if channel['min_revenue']:
            prob += x[i] * channel['ROAS'] >= channel['min_revenue'], f"MinRevenue{i}"

    status = prob.solve()

    if status != 1:
        st.warning("Optimal solution not found. Please adjust your constraints.")
        return None

    return [pulp.value(x_i) for x_i in x]

def main():
    st.title("Advertising Budget Allocation")
    budget = st.number_input("Overall budget", min_value=0, value=1000)
    min_channels = st.number_input("Minimum number of channels (optional)", min_value=1, value=None, key='min_channels')

    st.subheader("Channel Information")
    n_channels = st.number_input("Number of channels", min_value=2, value=2)

        channels = []

    for i in range(n_channels):
        st.subheader(f"Channel {i + 1}")
        name = st.text_input("Name", value=f"Channel {i + 1}", key=f"name{i}")
        ROAS = st.number_input("Historical ROAS", min_value=0.0, value=1.0, key=f"ROAS{i}")
        min_budget = st.number_input("Minimum budget constraint (optional)", min_value=0, value=None, key=f"min_budget{i}")
        max_budget = st.number_input("Maximum budget constraint (optional)", min_value=0, value=None, key=f"max_budget{i}")
        min_revenue = st.number_input("Minimum revenue constraint (optional)", min_value=0, value=None, key=f"min_revenue{i}")

        channels.append({
            'name': name,
            'ROAS': ROAS,
            'min_budget': min_budget,
            'max_budget': max_budget,
            'min_revenue': min_revenue
        })

    if st.button("Submit for calculation"):
        if min_channels is None:
            min_channels = 1

        allocation = allocate_budget(channels, budget, min_channels)

        if allocation is not None:
            st.subheader("Budget Allocation")
            for name, alloc in zip([c['name'] for c in channels], allocation):
                st.write(f"{name}: {alloc:.2f}")

            st.subheader("Overall Revenue")
            st.write(f"Expected: {sum([c['ROAS'] * alloc for c, alloc in zip(channels, allocation)]):.2f}")
            st.write(f"Even Split: {sum([c['ROAS'] * (budget / n_channels) for c in channels]):.2f}")

if __name__ == '__main__':
    main()
