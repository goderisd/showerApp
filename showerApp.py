import streamlit as st
import pandas as pd

# Load the invitee data
invitees_file = "invitees.csv"  # Replace with your actual file path
invitees_df = pd.read_csv(invitees_file)

# Name search bar
st.sidebar.header("Search Invitee")
search_name = st.sidebar.text_input("Enter Name")
filtered_invitees = invitees_df[invitees_df['Name'].str.contains(search_name, case=False, na=False)]

# Display search results
st.sidebar.write("Search Results:")
if not filtered_invitees.empty:
    st.sidebar.dataframe(filtered_invitees)

    # Select invitee from search results
    selected_invitee = st.sidebar.selectbox(
        "Select Invitee",
        options=filtered_invitees['Name'].tolist()
    )

    # Assign selected invitee as the giver
    if st.sidebar.button("Assign to Gift Entry"):
        st.session_state['selected_invitee'] = selected_invitee
else:
    st.sidebar.write("No results found.")

# Add new gift with selected invitee
st.sidebar.header("Add New Gift")
with st.sidebar.form(key='gift_form'):
    giver_name = st.text_input("Giver's Name", value=st.session_state.get('selected_invitee', ''))
    gift_item = st.text_input("Gift Item")
    value = st.number_input("Value", min_value=0.0, step=0.01)
    date_received = st.date_input("Date Received")
    thank_you_note = st.checkbox("Thank You Note Sent")
    submit_button = st.form_submit_button(label='Add Gift')

    if submit_button:
        new_gift = {
            "Giver": giver_name,
            "Gift": gift_item,
            "Value": value,
            "Date": date_received,
            "Thank You Note": thank_you_note
        }
        st.session_state['gifts'].append(new_gift)

# Display gifts
st.header("Wedding Gifts")
df = pd.DataFrame(st.session_state['gifts'])
st.dataframe(df)