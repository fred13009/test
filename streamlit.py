import streamlit as st
import pulp

st.title('Advertising Budget Allocator')

def optimize_budget(ad_channels, total_budget, use_channel_exposure_constraint, min_channels_used):
    # The optimize_budget function definition goes here. (Same as previously provided)

    # ...

    return allocated_budget, optimal_revenue, even_revenue, optimal_channels_used

# Form to get user inputs
with st.form(key='input_form'):
    # Get user input for the total budget
    total_budget = st.number_input("Enter the total advertising budget:", value=1000.0, step=100.0, format="%.2f")
    
    # Get user input for the number of channels
    num_channels = st.number_input("Enter the number of advertising channels:", value=1, step=1, min_value=1, format="%d")
    
    # Get user input for channel details
    ad_channels = {}
    for i in range(num_channels):
        st.write(f"Channel {i + 1}:")
        channel_name = st.text_input(f"Enter the name of channel {i + 1}:")
        return_on_investment = st.number_input(f"Enter the return on investment (ROI) for {channel_name}:", value=1.0, step=0.01, format="%.2f", key=f"roi_{i}")
        min_revenue = st.number_input(f"Enter the minimum revenue constraint for {channel_name} (leave blank for none):", value=None, allow_none=True, key=f"min_revenue_{i}")
        min_budget = st.number_input(f"Enter the minimum budget constraint for {channel_name} (leave blank for none):", value=None, allow_none=True, key=f"min_budget_{i}")
        max_budget = st.number_input(f"Enter the maximum budget constraint for {channel_name} (leave blank for none):", value=None, allow_none=True, key=f"max_budget_{i}")

        ad_channels[channel_name] = {
            "return_on_investment": return_on_investment,
            "min_revenue": min_revenue,
            "min_budget": min_budget,
            "max_budget": max_budget,
        }

    # Get user input for the optional channel exposure constraint
    use_channel_exposure_constraint = st.radio("Do you want to use a channel exposure constraint?", ("No", "Yes"))
    if use_channel_exposure_constraint == "Yes":
        min_channels_used = st.number_input("Enter the minimum number of channels to be used:", value=1, step=1, min_value=1, format="%d")
    else:
        min_channels_used = 0

    submit_button = st.form_submit_button("Submit Constraints")

if submit_button:
    allocated_budget, optimal_revenue, even_revenue, optimal_channels_used = optimize_budget(ad_channels, total_budget, use_channel_exposure_constraint, min_channels_used)

    # Display the results
    st.write("Optimal Allocation:", allocated_budget)
    st.write("Expected Revenue from Optimal Allocation:", optimal_revenue)
    st.write("Revenue from Even Budget Allocation:", even_revenue)
    st.write("Number of Channels Used in Optimal Allocation:", optimal_channels_used)
