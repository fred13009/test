import streamlit as st
from optimizer import optimize_budget

def app():
    st.set_page_config(page_title='Marketing Budget Allocation')

    st.title('Marketing Budget Allocation')

    channels = []
    channel_count = st.number_input('Number of Channels', min_value=1, max_value=10, value=1)
    for i in range(channel_count):
        channel_name = st.text_input(f'Channel {i + 1} Name')
        channel_roi = st.number_input(f'Historical ROI for Channel {i + 1}', min_value=0.0)
        channel_min_budget = st.number_input(f'Minimum Budget for Channel {i + 1}', min_value=0.0)
        channel_max_budget = st.number_input(f'Maximum Budget for Channel {i + 1}', min_value=0.0)
        channel_targeted_sales = st.number_input(f'Targeted Sales for Channel {i + 1} (optional)', min_value=0.0, value=0.0)
        channels.append({
            'name': channel_name,
            'roi': channel_roi,
            'minBudget': channel_min_budget,
            'maxBudget': channel_max_budget,
            'targetedSales': channel_targeted_sales
        })

    total_budget = st.number_input('Total Marketing Budget', min_value=0.0)

    if st.button('Calculate Allocation'):
        numeric_channels = []
        for channel in channels:
            numeric_channels.append({
                'name': channel['name'],
                'roi': float(channel['roi']),
                'minBudget': float(channel['minBudget']),
                'maxBudget': float(channel['maxBudget']),
                'targetedSales': float(channel['targetedSales'])
            })
        result = optimize_budget(numeric_channels, float(total_budget))
        if result['success']:
            st.header('Optimal Budget Allocation')
            allocation_table = []
            for i, channel_allocation in enumerate(result['allocation']):
                allocation_table.append([channels[i]['name'], f'${channel_allocation:,.2f}'])
            st.table(allocation_table)
        else:
            st.error(result['message'])
