import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# Title and Introduction
st.title('Advanced Marketing Budget Allocator Tool for Multi-Retailer Online Advertising')

# Input: Number of Retailers
num_retailers = st.number_input('Enter the number of retailers', min_value=1, step=1)

# Collecting Retailer Data
retailer_data = []
for i in range(num_retailers):
    st.subheader(f'Retailer {i+1} Details')
    name = st.text_input(f'Name of Retailer {i+1}', key=f'name_{i}')
    roi = st.number_input(f'Historical ROI for Retailer {i+1} (Revenue per Spend)', key=f'roi_{i}')
    min_spend = st.number_input(f'Minimum Spend for Retailer {i+1}', key=f'min_{i}', min_value=0.0)
    max_spend = st.number_input(f'Maximum Spend for Retailer {i+1}', key=f'max_{i}', min_value=0.0)
    min_revenue = st.number_input(f'Minimum Revenue for Retailer {i+1}', key=f'min_rev_{i}', min_value=0.0)
    max_revenue = st.number_input(f'Maximum Revenue for Retailer {i+1}', key=f'max_rev_{i}', min_value=0.0)
    retailer_data.append((name, roi, min_spend, max_spend, min_revenue, max_revenue))

# Total Budget Input
total_budget = st.number_input('Enter Total Advertising Budget', min_value=0.0)

# Function to perform budget allocation with optimization
def allocate_budget(retailer_data, total_budget):
    num_retailers = len(retailer_data)

    # Objective: Maximize total revenue (negative ROI because linprog does minimization)
    c = [-roi for _, roi, _, _, _, _ in retailer_data]

    # Constraints
    A = []
    b = []

    # Spend and Revenue constraints for each retailer
    for _, roi, min_spend, max_spend, min_revenue, max_revenue in retailer_data:
        # Spend constraints
        row = np.zeros(num_retailers)
        row[i] = 1
        if max_spend > 0:
            A.append(row)
            b.append(max_spend)
        if min_spend > 0:
            A.append(-row)
            b.append(-min_spend)

        # Revenue constraints
        if max_revenue > 0:
            A.append(-row * roi)
            b.append(-min_revenue)
        if min_revenue > 0:
            A.append(row * roi)
            b.append(max_revenue)

    # Total budget constraint
    A.append(np.ones(num_retailers))
    b.append(total_budget)

    # Optimization
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), method='highs')

    if res.success:
        return res.x
    else:
        raise ValueError("Optimization failed: " + res.message)

# Budget Allocation and Display Results
if st.button('Allocate Budget'):
    try:
        allocated_budgets = allocate_budget(retailer_data, total_budget)
        # Dataframe for displaying results
        df = pd.DataFrame(retailer_data, columns=['Retailer', 'Historical ROI', 'Min Spend', 'Max Spend', 'Min Revenue', 'Max Revenue'])
        df['Allocated Budget'] = allocated_budgets
        df['Expected Revenue'] = df['Allocated Budget'] * df['Historical ROI']

        st.dataframe(df)

        # Summary and Visualization
        st.subheader('Summary Dashboard')
        st.bar_chart(df[['Retailer', 'Allocated Budget']].set_index('Retailer'))

        # Total expected revenue
        total_revenue = df['Expected Revenue'].sum()
        st.write(f'Total Expected Revenue: ${total_revenue:.2f}')

    except Exception as e:
        st.error(f'Error in allocation: {e}')

# End of Streamlit App Code
