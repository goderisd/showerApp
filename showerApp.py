import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Wedding Gift Tracker", page_icon="💒", layout="wide")

# Add custom CSS for a festive theme
st.markdown("""
    <style>
        .main {
            background-color: #fff5f7;
        }
        h1, h2, h3, h4 {
            color: #e91e63;
        }
        .sidebar .sidebar-content {
            background-color: #fff0f3;
        }
        .stButton>button {
            background-color: #e91e63;
            color: white;
            border-radius: 10px;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for gifts if it doesn't exist
if 'gifts' not in st.session_state:
    st.session_state['gifts'] = []

# Load the invitee data
invitees_file = "invitees.csv"  # Replace with your actual file path
invitees_df = pd.read_csv(invitees_file)

# Name search bar in the sidebar
st.sidebar.header("Search Invitee")
search_name = st.sidebar.text_input("Enter First or Last Name")
filtered_invitees = invitees_df[
    invitees_df[['First Name', 'Last Name']].apply(lambda row: search_name.lower() in row.astype(str).str.lower().values, axis=1)
]

# Display search results in the main page
st.header("Search Results")
if not filtered_invitees.empty:
    st.dataframe(filtered_invitees)

    # Select invitee from search results
    selected_invitee = st.selectbox(
        "Select Invitee",
        options=filtered_invitees['First Name'] + " " + filtered_invitees['Last Name']
    )

    # Assign selected invitee as the giver
    if st.button("Assign to Gift Entry"):
        selected_row = filtered_invitees[
            (filtered_invitees['First Name'] + " " + filtered_invitees['Last Name']) == selected_invitee
        ].iloc[0]
        st.session_state['selected_invitee'] = {
            'First Name': selected_row['First Name'],
            'Last Name': selected_row['Last Name'],
            'Address': selected_row[['Street Address 1', 'Street Address 2', 'City', 'State/Province', 'Zip/Postal Code', 'Country']].to_dict(),
            'RSVP': selected_row[['Wedding Day - RSVP', 'Wedding Day - Gift Received']].to_dict()
        }
else:
    st.write("No results found.")

    # Button to reveal manual entry form
    if st.button("Add Person Manually"):
        with st.form(key='add_person_form'):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            street1 = st.text_input("Street Address 1")
            street2 = st.text_input("Street Address 2", value="")
            city = st.text_input("City")
            state = st.text_input("State/Province")
            zip_code = st.text_input("Zip/Postal Code")
            country = st.text_input("Country")
            add_person_button = st.form_submit_button(label='Add Person')

            if add_person_button:
                new_person = {
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Street Address 1": street1,
                    "Street Address 2": street2,
                    "City": city,
                    "State/Province": state,
                    "Zip/Postal Code": zip_code,
                    "Country": country
                }
                invitees_df = invitees_df.append(new_person, ignore_index=True)
                st.success("Person added successfully!")

# Add new gift with selected invitee
st.header("Add New Gift")
with st.form(key='gift_form'):
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
            "Thank You Note": thank_you_note,
            "Address": st.session_state.get('selected_invitee', {}).get('Address', {})
        }
        st.session_state['gifts'].append(new_gift)

# Display gifts
st.header("Wedding Gifts")
if len(st.session_state['gifts']) > 0:
    df = pd.DataFrame(st.session_state['gifts'])
    st.dataframe(df)
else:
    st.write("No gifts added yet.")

# Button to clear gifts with confirmation
if st.button("Clear Gifts Data"):
    if st.confirm("Are you sure you want to clear all gift data? This action cannot be undone."):
        st.session_state['gifts'] = []
        st.success("Gifts data cleared!")

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
