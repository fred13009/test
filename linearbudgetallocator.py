import pulp

# Get user input for the number of channels
num_channels = int(input("Enter the number of advertising channels: "))

# Get user input for channel details
ad_channels = {}
for i in range(num_channels):
    channel_name = input(f"Enter the name of channel {i+1}: ")
    return_on_investment = float(input(f"Enter the return on investment (ROI) for {channel_name}: "))
    
    min_revenue = input(f"Enter the minimum revenue constraint for {channel_name} (leave blank for none): ")
    if min_revenue:
        min_revenue = float(min_revenue)
    else:
        min_revenue = None
        
    min_budget = input(f"Enter the minimum budget constraint for {channel_name} (leave blank for none): ")
    if min_budget:
        min_budget = float(min_budget)
    else:
        min_budget = None

    max_budget = input(f"Enter the maximum budget constraint for {channel_name} (leave blank for none): ")
    if max_budget:
        max_budget = float(max_budget)
    else:
        max_budget = None

    ad_channels[channel_name] = {
        "return_on_investment": return_on_investment,
        "min_revenue": min_revenue,
        "min_budget": min_budget,
        "max_budget": max_budget,
    }

# Get user input for the total budget
total_budget = float(input("Enter the total advertising budget: "))

# Get user input for the optional channel exposure constraint
use_channel_exposure_constraint = input("Do you want to use a channel exposure constraint? (yes/no): ").lower()
if use_channel_exposure_constraint == "yes":
    min_channels_used = int(input("Enter the minimum number of channels to be used: "))
else:
    min_channels_used = 0

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

# Print the results
print("Optimal Allocation:", allocated_budget)
print("Expected Revenue from Optimal Allocation:", optimal_revenue)
print("Revenue from Even Budget Allocation:", even_revenue)
print("Number of Channels Used in Optimal Allocation:", optimal_channels_used)