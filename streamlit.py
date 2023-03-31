import streamlit as st
import pulp

# Initialize Streamlit app
st.set_page_config(page_title="Advertising Budget Allocation", page_icon=None, layout="centered", initial_sidebar_state="expanded")

st.title("Advertising Budget Allocation")

# Input overall budget
overall_budget = st.number_input("Enter your overall budget:", min_value=0, value=1000, step=1, format="%d")
st.markdown("---")

# Input optional channel exposure constraint
use_channel_exposure_constraint = st.checkbox("Use channel exposure constraint")
channel_exposure_constraint = None
if use_channel_exposure_constraint:
    channel_exposure_constraint = st.number_input("Enter minimum number of channels to use:", min_value=2, max_value=10, value=2, step=1, format="%d")

# Next step button
if st.button("Next Step"):
    st.session_state.overall_budget = overall_budget
    st.session_state.channel_exposure_constraint = channel_exposure_constraint
    st.session_state.next_step = True

# Start of the second part
def channel_input_form(channel_number):
    channel_name = st.text_input(f"Channel {channel_number} Name:", key=f"channel_{channel_number}_name")
    historical_roas = st.number_input(f"Channel {channel_number} Historical ROAS:", min_value=0.0, value=1.0, step=0.1, format="%.1f", key=f"channel_{channel_number}_roas")
    return {
        "name": channel_name,
        "roas": historical_roas,
    }

if "next_step" in st.session_state and st.session_state.next_step:
    st.markdown("---")
    st.header("How many channels do you want to cover?")
    st.session_state.num_channels = st.number_input("Number of channels:", min_value=2, max_value=10, value=2, step=1, format="%d")

    if st.button("Next Step Channels"):
        st.session_state.next_step_channels = True

if "next_step_channels" in st.session_state and st.session_state.next_step_channels:
    st.markdown("---")
    st.header("Marketing Channels")

    channels = []
    for i in range(1, st.session_state.num_channels + 1):
        channel = channel_input_form(i)
        channels.append(channel)

    # Move to the next part
    if st.button("Next Step Constraints"):
        st.session_state.channels = channels
        st.session_state.next_step_constraints = True

# Constraint input
if "next_step_constraints" in st.session_state and st.session_state.next_step_constraints:
    st.markdown("---")
    st.header("Marketing Channel Constraints")

    if "constraints" not in st.session_state:
        st.session_state.constraints = []

    if st.button("Set New Constraints"):
        constraint_channel = st.selectbox("Select Channel", [channel["name"] for channel in st.session_state.channels])
        constraint_type = st.selectbox("Constraint Type", ["Minimum Budget", "Maximum Budget", "Minimum Revenue"])
        constraint_value = st.number_input("Constraint Value:", min_value=0, value=0, step=1, format="%d")

        st.session_state.constraints.append({"channel": constraint_channel, "type": constraint_type, "value": constraint_value})
        st.write(f"Added {constraint_type} constraint for {constraint_channel}: {constraint_value}")

    if st.button("Save Constraints"):
        st.session_state.saved_constraints = True

    if st.button("Run Calculation"):
        st.session_state.run_calculation = True

# Run calculation
if "run_calculation" in st.session_state and st.session_state.run_calculation:
    st.markdown("---")
    st.header("Budget Allocation Results")
    st.write("Here you would display the results of the optimization using the pulp library.")
