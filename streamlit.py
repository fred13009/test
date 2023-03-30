import streamlit as st

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

def channel_input_form(channel_number):
    channel_name = st.text_input(f"Channel {channel_number} Name:", key=f"channel_{channel_number}_name")
    historical_roas = st.number_input(f"Channel {channel_number} Historical ROAS:", min_value=0.0, value=1.0, step=0.1, format="%.1f", key=f"channel_{channel_number}_roas")

    min_budget = st.number_input(f"Channel {channel_number} Minimum Budget (Optional):", min_value=0, value=0, step=1, format="%d", key=f"channel_{channel_number}_min_budget")
    max_budget = st.number_input(f"Channel {channel_number} Maximum Budget (Optional):", min_value=min_budget, value=1000, step=1, format="%d", key=f"channel_{channel_number}_max_budget")

    min_revenue = st.number_input(f"Channel {channel_number} Minimum Revenue (Optional):", min_value=0, value=0, step=1, format="%d", key=f"channel_{channel_number}_min_revenue")

    return {
        "name": channel_name,
        "roas": historical_roas,
        "min_budget": min_budget if min_budget > 0 else None,
        "max_budget": max_budget if max_budget > 0 else None,
        "min_revenue": min_revenue if min_revenue > 0 else None,
    }

if "next_step" in st.session_state and st.session_state.next_step:
    st.markdown("---")
    st.header("Marketing Channels")

    if "num_channels" not in st.session_state:
        st.session_state.num_channels = 2

    channels = []
    for i in range(1, st.session_state.num_channels + 1):
        channel = channel_input_form(i)
        channels.append(channel)

    # Run Calculation button (Main Call to Action)
    if st.button("Run Calculation"):
        st.session_state.channels = channels
        st.session_state.calculate = True

    # Add New Channels button (Optional Action)
    if st.button("Add New Channels"):
        new_channels = st.number_input("How many new channels do you want to add?", min_value=1, max_value=(10 - st.session_state.num_channels), value=1, step=1, format="%d")
        st.session_state.num_channels += new_channels
