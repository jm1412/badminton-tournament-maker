import streamlit as st
import requests

# Flask backend URL
BACKEND_URL = "http://127.0.0.1:5000"  # Update if hosted elsewhere

# Page configuration
st.set_page_config(page_title="🏸 Badminton Tournament Maker", layout="wide")

# Sidebar for navigation with tabs
st.sidebar.title("Navigation")

# Custom CSS for tabs style
st.markdown("""
    <style>
        .tab {
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            background-color: #f1f1f1;
            margin-right: 10px;
            cursor: pointer;
            border-radius: 5px;
        }
        .tab-selected {
            background-color: #0072bc;
            color: white;
        }
        .tabs-container {
            display: flex;
            flex-wrap: nowrap;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'selected_tournament' not in st.session_state:
    st.session_state.selected_tournament = None

# Tabs navigation
tabs = ["Home", "Tournaments", "Players", "Manage Tournament", "Create Tournament"]
selected_tab = st.sidebar.selectbox("Select Page", tabs)

# Update session state based on selected tab
if selected_tab != st.session_state.page:
    st.session_state.page = selected_tab
    st.session_state.selected_tournament = None

# Home Page
if st.session_state.page == "Home":
    st.title("🏸 Badminton Tournament Maker")
    st.write("Welcome to the Badminton Tournament Maker! Use the sidebar to navigate and manage your tournaments and players.")
    st.write("### Quick Links")
    if st.button("View Tournaments"):
        st.session_state.page = "Tournaments"
        st.experimental_set_query_params(page="Tournaments")
    if st.button("View Players"):
        st.session_state.page = "Players"
        st.experimental_set_query_params(page="Players")

# Tournaments Page
elif st.session_state.page == "Tournaments":
    st.title("🏸 Tournaments")

    # Search for tournaments
    search_query = st.text_input("Search Tournaments:")

    # Fetch and display ongoing tournaments
    st.write("### Ongoing Tournaments")
    response = requests.get(f"{BACKEND_URL}/tournaments?status=ongoing&search={search_query}")
    if response.status_code == 200:
        ongoing_tournaments = response.json()
        for tournament in ongoing_tournaments:
            if st.button(f"{tournament['name']} ({tournament['type']})", key=f"ongoing_{tournament['tournament_id']}"):
                st.session_state.page = "Tournament Details"
                st.session_state.selected_tournament = tournament['tournament_id']
                st.experimental_set_query_params(page="Tournament Details", tournament_id=tournament['tournament_id'])
    else:
        st.error("Failed to fetch ongoing tournaments.")

    # Fetch and display recent tournaments
    st.write("### Recent Tournaments")
    response = requests.get(f"{BACKEND_URL}/tournaments?status=recent&limit=5&search={search_query}")
    if response.status_code == 200:
        recent_tournaments = response.json()
        for tournament in recent_tournaments:
            if st.button(f"{tournament['name']} ({tournament['type']})", key=f"recent_{tournament['tournament_id']}"):
                st.session_state.page = "Tournament Details"
                st.session_state.selected_tournament = tournament['tournament_id']
                st.experimental_set_query_params(page="Tournament Details", tournament_id=tournament['tournament_id'])
    else:
        st.error("Failed to fetch recent tournaments.")

    # Button to navigate to Create Tournament page
    if st.button("Create a New Tournament"):
        st.session_state.page = "Create Tournament"
        st.experimental_set_query_params(page="Create Tournament")

# Create Tournament Page
elif st.session_state.page == "Create Tournament":
    st.title("🏸 Create a New Tournament")
    with st.form("create_tournament_form"):
        name = st.text_input("Tournament Name (no spaces):")
        categories = st.text_area("Categories (comma-separated):")
        date_from = st.date_input("Date of Play (From):")
        date_to = st.date_input("Date of Play (To):")
        courts = st.number_input("Number of Badminton Courts:", min_value=1, step=1)
        password = st.text_input("Set Admin Password:", type="password")
        type = st.radio("Tournament Type:", ("Singles", "Doubles"))
        submitted = st.form_submit_button("Create Tournament")
        if submitted:
            if name and categories and date_from and date_to and courts and password:
                response = requests.post(
                    f"{BACKEND_URL}/tournaments",
                    json={
                        "name": name,
                        "categories": categories.split(','),
                        "date_from": date_from.isoformat(),
                        "date_to": date_to.isoformat(),
                        "courts": courts,
                        "password": password,
                        "type": type
                    }
                )
                if response.status_code == 201:
                    st.success("Tournament created successfully!")
                else:
                    st.error("Failed to create tournament.")
            else:
                st.error("Please fill in all fields.")

# Tournament Details Page
elif st.session_state.page == "Tournament Details":
    tournament_id = st.session_state.selected_tournament
    if tournament_id:
        response = requests.get(f"{BACKEND_URL}/tournaments/{tournament_id}")
        if response.status_code == 200:
            tournament = response.json()
            st.title(f"🏸 {tournament['name']}")
            st.write(f"Type: {tournament['type']}")
            st.write(f"Dates: {tournament['date_from']} to {tournament['date_to']}")
            st.write(f"Categories: {', '.join(tournament['categories'].split(','))}")
            st.write(f"Courts: {tournament['courts']}")
            participants = tournament.get('participants', [])
            if participants:
                st.write(f"Participants: {', '.join(participants)}")
            else:
                st.write("Participants: None")
            if st.button("Back"):
                st.session_state.page = "Tournaments"
                st.session_state.selected_tournament = None
                st.experimental_set_query_params(page="Tournaments")
        else:
            st.error("Failed to fetch tournament details.")
    else:
        st.error("No tournament selected.")
