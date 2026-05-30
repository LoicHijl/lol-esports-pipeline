import json
import os
import sys
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials

wiki_user = os.getenv("WIKI_USER")
wiki_pass = os.getenv("WIKI_PASS")

credentials = AuthCredentials(
    username = wiki_user,
    password = wiki_pass
)

if not wiki_pass or not wiki_user:
    print("ERROR: Missing environment variables! Please set WIKI_USER and WIKI_PASS")
    sys.exit(1)

def fetch_tournament_data(tournament_name):
    # Connect to the Leaguepedia MediaWiki instance
    site = EsportsClient("lol", credentials=credentials)

    print(f"Connecting to Leaguepedia to fetch data for: {tournament_name}...")

    # Query the Cargo database
    response = site.cargo_client.query(
        tables = "ScoreboardGames=SG, Tournaments=T",
        join_on = "SG.OverviewPage=T.OverviewPage",
        fields = ", SG.DateTime_UTC, SG.Team1, " \
        "SG.Team2, SG.WinTeam, SG.Gamelength, " \
        "SG.Team1Bans, SG.Team2Bans, SG.Team1Picks, " \
        "SG.Team2Picks, SG.Team1Gold, SG.Team2Gold",
        where = f"SG.OverviewPage LIKE '%{tournament_name}%'",
        order_by = "SG.DateTime_UTC"
    )

    return response

def save_raw_data(data, filename="raw_msi_games.json"):
    os.makedirs("data/raw", exist_ok=True)
    filepath = os.path.join("data/raw", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully saved {len(data)} games to {filepath}.")

if __name__ == "__main__":
    target_tournament = "2025 Season World Championship"

    try:
        raw_games = fetch_tournament_data(target_tournament)
        if raw_games:
            save_raw_data(raw_games)
        else:
            print("No games found")
    except Exception as e:
        print(f"An error occured: {e}")

    