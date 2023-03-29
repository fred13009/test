import streamlit as st
import pulp

def optimize_budget(ad_channels, total_budget, use_channel_exposure_constraint, min_channels_used):
    # ... (the rest of the script logic goes here, excluding user inputs)

    return allocated_budget, optimal_revenue, even_revenue, optimal_channels_used

# Add Streamlit code to create the user interface for the app
st.title('Advertising Budget Allocator')

# Get user input for the number of channels
num_channels = st.number_input("Enter the number of advertising channels:", min_value=1, value=1, step=1, format="%d")

# Get user input for channel details
ad_channels = {}
for i in range(num_channels):
    channel_name = st.text_input(f"Enter the name of channel {i+1}: ")
    return_on_investment = st.number_input(f"Enter the return on investment (ROI) for {channel_name}:", value=1.0, step=0.01, format="%.2f")
    
    min_revenue = st.text_input(f"Enter the minimum revenue constraint for {channel_name} (leave blank for none): ")
    min_revenue = float(min_revenue) if min_revenue.strip() else None
    
    min_budget = st.text_input(f"Enter the minimum budget constraint for {channel_name} (leave blank for none): ")
    min_budget = float(min_budget) if min_budget.strip() else None
    
    max_budget = st.text_input(f"Enter the maximum budget constraint for {channel_name} (leave blank for none): ")
    max_budget = float(max_budget) if max_budget.strip() else None

    ad_channels[channel_name] = {
        "return_on_investment": return_on_investment,
        "min_revenue": min_revenue,
        "min_budget": min_budget,
        "max_budget": max_budget,
    }

# Get user input for the total budget
total_budget = st.number_input("Enter the total advertising budget:", value=1.0, step=0.01, format="%.2f")

# Get user input for the optional channel exposure constraint
use_channel_exposure_constraint = st.selectbox("Do you want to use a channel exposure constraint?", options=["no", "yes"])
if use_channel_exposure_constraint == "yes":
    min_channels_used = st.number_input("Enter the minimum number of channels to be used:", min_value=1, value=1, step=1, format="%d")
else:
    min_channels_used = 0

if st.button("Calculate Budget Allocation"):
    allocated_budget, optimal_revenue, even_revenue, optimal_channels_used = optimize_budget(ad_channels, total_budget, use_channel_exposure_constraint, min_channels_used)

    st.write("Optimal Allocation:", allocated_budget)
    st.write("Expected Revenue from Optimal Allocation:", optimal_revenue)
    st.write("Revenue from Even Budget Allocation:", even_revenue)
    st.write("Number of Channels Used in Optimal Allocation:", optimal_channels_used)
