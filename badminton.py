import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Constants for file paths
TOURNAMENTS_DIR = "tournaments"
PLAYERS_FILE = "players.json"

# Ensure directories exist
os.makedirs(TOURNAMENTS_DIR, exist_ok=True)
if not os.path.exists(PLAYERS_FILE):
    with open(PLAYERS_FILE, "w") as f:
        json.dump({}, f)

# Utility functions
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def get_tournament_file(tournament_id):
    return os.path.join(TOURNAMENTS_DIR, f"{tournament_id}.json")

# Load player data
players = load_json(PLAYERS_FILE)

# Streamlit app
st.title("Badminton Tournament Manager")

# Tournament Management
st.header("Tournament Management")
tournament_id = st.text_input("Enter Tournament ID (or create a new one):")

if tournament_id:
    tournament_file = get_tournament_file(tournament_id)
    tournament_data = load_json(tournament_file)

    if not tournament_data:
        st.write("Creating a new tournament...")
        tournament_name = st.text_input("Tournament Name:")
        num_courts = st.number_input("Number of Courts:", min_value=1, step=1)

        if st.button("Create Tournament"):
            tournament_data = {
                "name": tournament_name,
                "num_courts": num_courts,
                "players": [],
                "matches": [],
                "brackets": []
            }
            save_json(tournament_file, tournament_data)
            st.success("Tournament created successfully!")
    else:
        st.write(f"Tournament Name: {tournament_data['name']}")
        st.write(f"Number of Courts: {tournament_data['num_courts']}")

        # Player Management
        st.subheader("Player Management")
        player_name = st.text_input("Enter Player Name:")
        skill_level = st.selectbox("Select Skill Level:", ["Beginner", "Intermediate", "Advanced"])

        if st.button("Add Player"):
            player_id = player_name.replace(" ", "_").lower()

            if player_id not in players:
                players[player_id] = {
                    "name": player_name,
                    "history": []
                }
                save_json(PLAYERS_FILE, players)

            tournament_data["players"].append({
                "id": player_id,
                "name": player_name,
                "skill_level": skill_level
            })
            save_json(tournament_file, tournament_data)
            st.success(f"Player {player_name} added to the tournament!")

        st.write("### Players in this Tournament:")
        for player in tournament_data["players"]:
            st.write(f"- {player['name']} ({player['skill_level']})")

        # Match Scheduling
        st.subheader("Match Scheduling")
        match_day = st.date_input("Select Match Day:")
        start_time = st.time_input("Start Time:")
        game_duration = st.number_input("Game Duration (minutes):", min_value=1, step=1)

        if st.button("Generate Schedule"):
            schedule = []
            current_time = datetime.combine(match_day, start_time)

            for i, player in enumerate(tournament_data["players"]):
                opponent = tournament_data["players"][(i + 1) % len(tournament_data["players"])]
                schedule.append({
                    "player1": player["name"],
                    "player2": opponent["name"],
                    "time": current_time.strftime("%Y-%m-%d %H:%M")
                })
                current_time += timedelta(minutes=game_duration)

            tournament_data["matches"] = schedule
            save_json(tournament_file, tournament_data)
            st.success("Schedule generated successfully!")

        st.write("### Match Schedule:")
        for match in tournament_data.get("matches", []):
            st.write(f"{match['time']}: {match['player1']} vs {match['player2']}")

        # Enter Match Results
        st.subheader("Enter Match Results")
        for match in tournament_data.get("matches", []):
            st.write(f"{match['player1']} vs {match['player2']}")
            player1_score = st.number_input(f"{match['player1']} Score:", key=f"{match['player1']}_score")
            player2_score = st.number_input(f"{match['player2']} Score:", key=f"{match['player2']}_score")

            if st.button(f"Submit Result for {match['player1']} vs {match['player2']}", key=f"submit_{match['player1']}_{match['player2']}"):
                winner = match['player1'] if player1_score > player2_score else match['player2']
                players[match['player1']]["history"].append({
                    "opponent": match['player2'],
                    "score": f"{player1_score}-{player2_score}",
                    "result": "Win" if player1_score > player2_score else "Loss"
                })
                players[match['player2']]["history"].append({
                    "opponent": match['player1'],
                    "score": f"{player2_score}-{player1_score}",
                    "result": "Win" if player2_score > player1_score else "Loss"
                })
                save_json(PLAYERS_FILE, players)
                st.success(f"Result submitted: {winner} wins!")

# Player Search
st.header("Search Player History")
search_player = st.text_input("Enter Player Name to Search:")
if st.button("Search Player"):
    player_id = search_player.replace(" ", "_").lower()
    if player_id in players:
        st.write(f"### Match History for {players[player_id]['name']}")
        for match in players[player_id]["history"]:
            st.write(f"- vs {match['opponent']}: {match['score']} ({match['result']})")
    else:
        st.error("Player not found!")
