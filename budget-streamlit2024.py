import streamlit as st
import pandas as pd
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
    rev_threshold = st.number_input(f'Revenue Threshold for Retailer {i+1}', key=f'rev_{i}', min_value=0.0)
    retailer_data.append((name, roi, min_spend, max_spend, rev_threshold))

# Total Budget Input
total_budget = st.number_input('Enter Total Advertising Budget', min_value=0.0)

# Function to perform budget allocation with optimization
def allocate_budget(retailer_data, total_budget):
    num_retailers = len(retailer_data)

    # Objective: Maximize total revenue (negative ROI because linprog does minimization)
    c = [-roi for _, roi, _, _, _ in retailer_data]

    # Constraints
    # Upper bounds for spends on each retailer (if max_spend is zero, use a large number to mimic 'no upper limit')
    A_ub = np.identity(num_retailers)
    b_ub = [max_spend if max_spend > 0 else 1e9 for _, _, _, max_spend, _ in retailer_data]

    # Lower bounds for spends on each retailer
    A_lb = -np.identity(num_retailers)
    b_lb = [-min_spend for _, _, min_spend, _, _ in retailer_data]

    # Total budget constraint
    A_eq = [np.ones(num_retailers)]
    b_eq = [total_budget]

    # Combine constraints
    A = np.vstack([A_ub, A_lb])
    b = np.concatenate([b_ub, b_lb])

    # Optimization
    res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, method='highs')

    if res.success:
        return res.x
    else:
        raise ValueError("Optimization failed: " + res.message)

# Budget Allocation and Display Results
if st.button('Allocate Budget'):
    try:
        allocated_budgets = allocate_budget(retailer_data, total_budget)
        # Dataframe for displaying results
        df = pd.DataFrame(retailer_data, columns=['Retailer', 'Historical ROI', 'Min Spend', 'Max Spend', 'Revenue Threshold'])
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
