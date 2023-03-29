import streamlit as st
import pulp

def optimize_budget(ad_channels, total_budget, use_channel_exposure_constraint, min_channels_used):
    # Create the LP problem
    prob = pulp.LpProblem("AdvertisingBudgetAllocation", pulp.LpMaximize)

    # Define the decision variables
    allocations = pulp.LpVariable.dicts("alloc", ad_channels.keys(), lowBound=0, cat="Continuous")
    channel_used = pulp.LpVariable.dicts("used", ad_channels.keys(), cat="Binary")

    # Define the objective function (maximize the total revenue)
    prob += pulp.lpSum([allocations[channel] * data["return_on_investment"] for channel, data in ad_channels.items()])

    # Add the total budget constraint
    prob += pulp.lpSum([allocations[channel] for channel in ad_channels.keys()]) <= total_budget

    # Add the channel-specific minimum and maximum budget constraints
    for channel, data in ad_channels.items():
        if data["min_budget"] is not None:
            prob += allocations[channel] >= data["min_budget"]
        if data["max_budget"] is not None:
            prob += allocations[channel] <= data["max_budget"]

    # Add the channel-specific minimum revenue constraints
    for channel, data in ad_channels.items():
        if data["min_revenue"] is not None:
            prob += allocations[channel] * data["return_on_investment"] >= data["min_revenue"]

    # Add the channel exposure constraint (minimum number of channels used)
    if use_channel_exposure_constraint == "yes":
        prob += pulp.lpSum([channel_used[channel] for channel in ad_channels.keys()]) >= min_channels_used

        # Link the binary decision variables to the corresponding allocation variables
        for channel in ad_channels.keys():
            prob += allocations[channel] <= channel_used[channel] * total_budget

    # Solve the problem
    prob.solve()

    # Get the optimal allocation and calculate the revenues
    allocated_budget = {channel: pulp.value(allocations[channel]) for channel in ad_channels.keys()}
    optimal_revenue = sum([allocated_budget[channel] * ad_channels[channel]["return_on_investment"] for channel in ad_channels.keys()])
    even_budget = total_budget / len(ad_channels)
    even_revenue = sum([even_budget * ad_channels[channel]["return_on_investment"] for channel in ad_channels.keys()])
    optimal_channels_used = sum([1 for channel in ad_channels.keys() if allocated_budget[channel] > 0])

    return allocated_budget, optimal_revenue, even_revenue, optimal_channels_used


st.title('Advertising Budget Allocator')

# Get user input for the total budget
total_budget = st.number_input("Enter the total advertising budget:", value=1.0, step=0.01, format="%.2f")

# Get user input for the number of channels
num_channels = st.number_input("Enter the number of advertising channels:", min_value=1, value=1, step=1, format="%d", key="num_channels")

with st.form("channel_form"):
    # Get user input for channel details
    ad_channels = {}
    for i in range(num_channels):
        with st.expander(f"Channel {i+1}"):
            channel_name = st.text_input(f"Enter the name of channel {i+1}: ", key=f"channel_name_{i}")
            return_on_investment = st.number_input(f"Enter the return on investment (ROI) for {channel_name}:", value=1.0, step=0.01, format="%.2f", key=f"roi_{i}")
            
            min_revenue = st.text_input(f"Enter the minimum revenue constraint for {channel_name} (leave blank for none): ", key=f"min_revenue_{i}")
            min_revenue = float(min_revenue) if min_revenue.strip() else None
            
            min_budget = st.text_input(f"Enter the minimum budget constraint for {channel_name} (leave blank for none): ", key=f"min_budget_{i}")
            min_budget = float(min_budget) if min_budget.strip() else None
            
            max_budget = st.text_input(f"Enter the maximum budget constraint for {channel_name} (leave blank for none): ", key=f"max_budget_{i}")
            max_budget = float(max_budget) if max_budget.strip() else None

            ad_channels[channel_name] = {
                "return_on_investment": return_on_investment,
                "min_revenue": min_revenue,
                "min_budget": min_budget,
                "max_budget": max_budget,
            }

    # Get user input for the optional channel exposure constraint
    use_channel_exposure_constraint = st.selectbox("Do you want to use a channel exposure constraint?", options=["no", "yes"], key="exposure_constraint")
    if use_channel_exposure_constraint == "yes":
        min_channels_used = st.number_input("Enter the minimum number of channels to be used:", min_value=1, value=1, step=1, format="%d", key="min_channels_used")
    else:
        min_channels_used = 0

    submit_button = st.form_submit_button("Calculate Budget Allocation")

if submit_button:
    allocated_budget, optimal_revenue, even_revenue, optimal_channels_used = optimize_budget(ad_channels, total_budget, use_channel_exposure_constraint, min_channels_used)

    st.write("Optimal Allocation:", allocated_budget)
    st.write("Expected Revenue from Optimal Allocation:", optimal_revenue)
    st.write("Revenue from Even Budget Allocation:", even_revenue)
    st.write("Number of Channels Used in Optimal Allocation:", optimal_channels_used)
