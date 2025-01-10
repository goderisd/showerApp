import streamlit as st
import pandas as pd

# Load the invitee data
invitees_file = "invitees.csv"  # Replace with your actual file path
invitees_df = pd.read_csv(invitees_file)

# Name search bar
st.sidebar.header("Search Invitee")
search_name = st.sidebar.text_input("Enter First or Last Name")
filtered_invitees = invitees_df[
    invitees_df[['First Name', 'Last Name']].apply(lambda row: search_name.lower() in row.astype(str).str.lower().values, axis=1)
]

# Display search results
st.sidebar.write("Search Results:")
if not filtered_invitees.empty:
    st.sidebar.dataframe(filtered_invitees)

    # Select invitee from search results
    selected_invitee = st.sidebar.selectbox(
        "Select Invitee",
        options=filtered_invitees['First Name'] + " " + filtered_invitees['Last Name']
    )

    # Assign selected invitee as the giver
    if st.sidebar.button("Assign to Gift Entry"):
        selected_row = filtered_invitees[
            (filtered_invitees['First Name'] + " " + filtered_invitees['Last Name']) == selected_invitee
        ].iloc[0]
        st.session_state['selected_invitee'] = {
            'First Name': selected_row['First Name'],
            'Last Name': selected_row['Last Name'],
            'Address': selected_row[['Street Address 1', 'Street Address 2', 'City', 'State/Province', 'Zip/Postal Code', 'Country']].to_dict(),
            'RSVP': selected_row[['Wedding Day - RSVP', 'Wedding Day - Gift Received']].to_dict()
        }

# Add new gift with selected invitee
st.sidebar.header("Add New Gift")
with st.sidebar.form(key='gift_form'):
    giver_name = st.text_input("Giver's Name", value=f"{st.session_state.get('selected_invitee', {}).get('First Name', '')} {st.session_state.get('selected_invitee', {}).get('Last Name', '')}")
    gift_item = st.text_input("Gift Item")
    value = st.number_input("Value", min_value=0.0, step=0.01)
    date_received = st.date_input("Date Received")
    thank_you_note = st.checkbox("Thank You Note Sent")
    submit_button = st.form_submit_button(label='Add Gift')

    if submit_button:
        new_gift = {
            "Giver": giver_name.strip(),
            "Gift": gift_item,
            "Value": value,
            "Date": date_received,
            "Thank You Note": thank_you_note
        }
        st.session_state['gifts'].append(new_gift)

        # Update invitee status
        if 'selected_invitee' in st.session_state:
            st.session_state['selected_invitee']['RSVP']['Wedding Day - Gift Received'] = True

# Display gifts
st.header("Wedding Gifts")
df = pd.DataFrame(st.session_state['gifts'])
st.dataframe(df)

# Download gifts as CSV
st.download_button("Download Gifts as CSV", df.to_csv(index=False), "wedding_gifts.csv", "text/csv")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    uploaded_df = pd.read_csv(uploaded_file)
    st.session_state['gifts'].extend(uploaded_df.to_dict('records'))

# Summary
st.sidebar.header("Summary")
total_gifts = len(st.session_state['gifts'])
total_value = sum(gift["Value"] for gift in st.session_state['gifts'])
st.sidebar.write(f"Total Gifts: {total_gifts}")
st.sidebar.write(f"Total Value: ${total_value:.2f}")
