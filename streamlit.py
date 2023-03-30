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
    # The rest of the main function remains unchanged

if __name__ == '__main__':
    main()
