import os
import requests
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

# Mapping for top 5 leagues
TOP_LEAGUES = {
    "Premier League": 2021,
    "La Liga": 2014,
    "Serie A": 2019,
    "Bundesliga": 2002,
    "Ligue 1": 2015
}

@app.route("/")
def index():
    """
    Render the main page with the dropdown for leagues.
    """
    leagues = list(TOP_LEAGUES.keys())  # for display in dropdown
    return render_template("index.html", leagues=leagues)

@app.route("/api/standings")
def get_standings():
    """
    Returns the standings for a given league ID as JSON.
    Expects a query param ?league=Premier%20League, etc.
    """
    league_name = request.args.get("league")
    if not league_name or league_name not in TOP_LEAGUES:
        return jsonify({"error": "Invalid or missing league"}), 400

    league_id = TOP_LEAGUES[league_name]
    url = f"{BASE_URL}/competitions/{league_id}/standings"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return jsonify({"error": f"Failed to fetch standings. Status: {r.status_code}"}), r.status_code

    data = r.json()
    standings_list = []

    # The first standings table is typically the league table
    if "standings" in data and data["standings"]:
        table = data["standings"][0].get("table", [])
        for row in table:
            standings_list.append({
                "position": row["position"],
                "team": row["team"]["name"],
                "played": row["playedGames"],
                "won": row["won"],
                "draw": row["draw"],
                "lost": row["lost"],
                "points": row["points"],
                "goalsFor": row["goalsFor"],
                "goalsAgainst": row["goalsAgainst"]
            })

    return jsonify({"standings": standings_list})

@app.route("/api/scorers")
def get_scorers():
    """
    Returns top scorers for a given league.
    Expects a query param ?league=Premier%20League
    """
    league_name = request.args.get("league")
    if not league_name or league_name not in TOP_LEAGUES:
        return jsonify({"error": "Invalid or missing league"}), 400

    league_id = TOP_LEAGUES[league_name]
    url = f"{BASE_URL}/competitions/{league_id}/scorers"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return jsonify({"error": f"Failed to fetch scorers. Status: {r.status_code}"}), r.status_code

    data = r.json()
    scorers_list = []

    if "scorers" in data:
        for scorer in data["scorers"]:
            scorers_list.append({
                "player": scorer["player"]["name"],
                "team": scorer["team"]["name"],
                "goals": scorer["goals"]
            })

    return jsonify({"scorers": scorers_list})

if __name__ == "__main__":
    # Run the Flask app (debug mode optional)
    app.run(debug=True)
