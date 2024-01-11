import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

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

# Function to perform linear regression-based allocation
def allocate_budget(retailer_data, total_budget):
    # Preparing data for linear regression
    X = []
    y = []
    constraints = []
    for name, roi, min_spend, max_spend, rev_threshold in retailer_data:
        X.append([roi])
        y.append(rev_threshold)
        constraints.append((min_spend, max_spend))

    # Linear Regression Model
    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)

    # Allocating budget based on model predictions and constraints
    allocated_budget = np.array([max(min(max_spend if max_spend > 0 else float('inf'), prediction), min_spend) for prediction, (min_spend, max_spend) in zip(predictions, constraints)])
    
    # Check if the sum of minimum constraints exceeds total budget
    if allocated_budget.sum() > total_budget:
        return None, "Constraints exceed total budget. Adjust constraints or increase total budget."

    # Adjusting the allocated budget to match the total budget
    sum_allocated = allocated_budget.sum()
    if sum_allocated != total_budget:
        scale = total_budget / sum_allocated
        allocated_budget *= scale

    return allocated_budget, None

# Budget Allocation and Display Results
if st.button('Allocate Budget'):
    allocated_budget, warning_message = allocate_budget(retailer_data, total_budget)
    
    if warning_message:
        st.warning(warning_message)
    else:
        # Dataframe for displaying results
        df = pd.DataFrame(retailer_data, columns=['Retailer', 'Historical ROI', 'Min Spend', 'Max Spend', 'Revenue Threshold'])
        df['Allocated Budget'] = allocated_budget
        df['Expected Revenue'] = df['Allocated Budget'] * df['Historical ROI']

        st.dataframe(df)

        # Summary Dashboard
        st.subheader('Summary Dashboard')
        fig, ax = plt.subplots()
        ax.bar(df['Retailer'], df['Allocated Budget'])
        st.pyplot(fig)

        # Total expected revenue
        total_revenue = df['Expected Revenue'].sum()
        st.write(f'Total Expected Revenue: ${total_revenue:.2f}')

# End of Streamlit App Code
