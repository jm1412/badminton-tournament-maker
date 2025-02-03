import streamlit as st
import requests

# Flask backend URL
BACKEND_URL = "https://juansymontano.eu.pythonanywhere.com/"

st.title("🏸 Badminton Tournament Maker")

# Fetch tournaments from backend
st.write("### Tournaments")
response = requests.get(f"{BACKEND_URL}/tournaments")
if response.status_code == 200:
    tournaments = response.json()
    for tournament in tournaments:
        st.write(f"- {tournament['name']} ({tournament['type']})")
else:
    st.error("Failed to fetch tournaments.")

# Create a new tournament
st.write("### Create a New Tournament")
name = st.text_input("Tournament Name (no spaces):")
type = st.radio("Tournament Type:", ("Singles", "Doubles"))
password = st.text_input("Set Admin Password:", type="password")

if st.button("Create Tournament"):
    if name and password:
        response = requests.post(
            f"{BACKEND_URL}/tournaments",
            json={"name": name, "type": type, "password": password}
        )
        if response.status_code == 201:
            st.success("Tournament created successfully!")
        else:
            st.error("Failed to create tournament.")
    else:
        st.error("Please fill in all fields.")

# Add a player
st.write("### Add a Player")
player_name = st.text_input("Player Name:")

if st.button("Add Player"):
    if player_name:
        response = requests.post(
            f"{BACKEND_URL}/players",
            json={"name": player_name}
        )
        if response.status_code == 201:
            st.success("Player added successfully!")
        else:
            st.error("Failed to add player.")
    else:
        st.error("Please enter a player name.")

# Fetch players
st.write("### Players")
response = requests.get(f"{BACKEND_URL}/players")
if response.status_code == 200:
    players = response.json()
    for player in players:
        st.write(f"- {player['name']}")
else:
    st.error("Failed to fetch players.")