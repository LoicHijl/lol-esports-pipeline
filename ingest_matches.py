import json
import os
import sys
import time
import boto3
import random
from datetime import datetime, timezone
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials

# Get environment variables
WIKI_USER = os.getenv("WIKI_USER")
WIKI_PASS = os.getenv("WIKI_PASS")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")

# Setup authentication for the MediaWiki API
credentials = AuthCredentials(
    username = WIKI_USER,
    password = WIKI_PASS
)

# Check verification and close (Important for Docker usage)
if not all([WIKI_PASS, WIKI_USER, AWS_KEY, AWS_SECRET,AWS_REGION]):
    print("ERROR: Missing environment variables!")
    sys.exit(1)

# Fetch the cargo data from a tournament
def fetch_tournament_data(site = None):
    # Fallback condition if no site instance was passed
    if site is None:
        print("No active session passed in. Creating a new EsportsClient connection.....")
        # Connect to the Leaguepedia MediaWiki instance
        site = EsportsClient("lol", credentials=credentials)

    tournament_name = "2025 Season World Championship"
    # Query the Cargo database
    response = fetch_cargo_data(
        tables = "ScoreboardGames=SG, Tournaments=T",
        fields = ", SG.DateTime_UTC, SG.Team1, " \
        "SG.Team2, SG.WinTeam, SG.Gamelength, " \
        "SG.Team1Bans, SG.Team2Bans, SG.Team1Picks, " \
        "SG.Team2Picks, SG.Team1Gold, SG.Team2Gold",
        condition = f"SG.OverviewPage LIKE '%{tournament_name}%'",
        site=site,
        join_on = "SG.OverviewPage=T.OverviewPage",
        order_by = "SG.DateTime_UTC"
    )

    return response

# Fetch any data from the cargo tables of the MediaWiki API
def fetch_cargo_data(tables, fields, condition = None, site = None, **kwargs):
    """Fetch any type of data from the cargo tables of the MediaWiki site instance"""
    # Fallback condition if no site instance was passed
    if site is None:
        print("No active session passed in. Creating a new EsportsClient connection...")
        # Connect to the Leaguepedia MediaWiki instance
        site = EsportsClient("lol", credentials=credentials)

    if condition is None:
        print(f"Fetching [{fields}] from [{tables}]")
    else:
        print(f"Fetching [{fields}] from [{tables}] with condition: {condition}")

    # Get the response from MediaWiki API
    response = site.cargo_client.query(
        tables=tables,
        fields=fields,
        where=condition,
        **kwargs
    )

    return response

# Store file locally
def save_raw_data(data, filename = "raw_msi_games.json"):
    os.makedirs("data/raw", exist_ok=True)
    filepath = os.path.join("data/raw", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully saved {len(data)} games to {filepath}.")

# Load data from local file
def load_data(filename = "raw_msi_games.json"):
    os.makedirs("data/raw", exist_ok=True)
    filepath = os.path.join("data/raw", filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data
    
# Upload some data to an s3 bucket
def upload_to_s3(data, file_tag = "games", bucket_name = "lol-esports-raw-data-688600819773-eu-central-1-an"):
    if not data:
        return
    print("Connecting to AWS S3...")
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    data = json.dumps(data, indent=4)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"raw/{file_tag}_{timestamp}.json"
    print(f"Uploading to s3://{bucket_name}/{file_name}")
    s3_client.put_object(
        Bucket = bucket_name,
        Key = file_name,
        Body = data,
        ContentType = "application/json"
    )
    print("The data has landed in the cloud!")

# Fetch either the dataset for players or for games (default games)
def fetch_dataset(games = True):
    if games:
        return fetch_dataset_games()
    else:
        return fetch_dataset_players()

# Fetch a dataset for players (using default fields)
def fetch_dataset_players(condition = "DateTime_UTC >= '2026-01-01 00:00:00'", condition_end = ""):
    # Start our session
    site = EsportsClient("lol", credentials=credentials)

    initial_condition = condition + condition_end

    # Fetch player data
    datas = fetch_cargo_data(
        site = site,
        tables = "ScoreboardPlayers",
        fields = "GameId, MatchId, " \
        "Name, Champion, Kills, Deaths, Assists, " \
        "SummonerSpells, Gold, CS, DamageToChampions, " \
        "Items, Team, DateTime_UTC, Role, " \
        "Role_Number, Side",
        condition = initial_condition,
        order_by = "DateTime_UTC",
        limit=100
    )

# Fetch a dataset for games (using default fields)
# Optional filter_end: Remember leading whitespace and " AND DateTime_UTC < '2026-01-01 00:00:00'"
def fetch_dataset_games(save_file_name = "raw_games_26", condition = "DateTime_UTC >= '2026-01-01 00:00:00'", condition_end = "", save_freq = 5):
    # Start our session
    site = EsportsClient("lol", credentials=credentials)

    initial_condition = condition + condition_end

    # Fetch games data
    datas = fetch_cargo_data(
        site = site,
        tables = "ScoreboardGames",
        fields = "GameId, MatchId, " \
        "Tournament, Team1, Team2, WinTeam, LossTeam, " \
        "DateTime_UTC, Gamelength_Number, Team1Bans, Team2Bans, " \
        "Team1Picks, Team2Picks, Team1Players, Team2Players, " \
        "Team1Gold, Team2Gold, Team1Kills, Team2Kills, Patch, ",
        condition = initial_condition,
        order_by = "DateTime_UTC",
        limit=100
    )

    # Initialize counter and data-holder
    pass_no = 0
    prev_data = None

    # Loop over all data
    while datas:
        # Create filename for intermediate storage
        filename = f"{save_file_name}_{pass_no}.json"

        # Increment counter
        pass_no += 1

        # Start new interval from last UTC timestamp
        dt_new = datas[-1]["DateTime UTC"]
        new_condition = f"DateTime_UTC > '{dt_new}'{condition_end}"

        # Save data
        if prev_data:
            # Save once every few passes
            if pass_no % save_freq == 0:
                prev_data = prev_data + datas
                
                save_raw_data(data=prev_data, filename=filename)
        else:
            print("Creating prev_data")
            prev_data = datas
            save_raw_data(data=datas, filename=filename)

        # Set random timeout to not overload API
        to = random.randint(5,60)
        print(f"[{pass_no}]: Chosen to wait {to} seconds...")
        time.sleep(to)

        # Fetch new data with new filter
        datas = fetch_cargo_data(
            site = site,
            tables = "ScoreboardPlayers",
            fields = "GameId, MatchId, " \
            "Name, Champion, Kills, Deaths, Assists, " \
            "SummonerSpells, Gold, CS, DamageToChampions, " \
            "Items, Team, DateTime_UTC, Role, " \
            "Role_Number, Side",
            condition = new_condition,
            order_by = "DateTime_UTC",
            limit=100
        )

    # Once no more new data is added, we are done
    print("Done with the loop")
    return prev_data

# Handle the uploads of the raw data
def do_uploads():
    games_tag = "raw_games_"
    players_tag = "raw_players_"

    for x in [25,26]:
        games_str = f"{games_tag}{x}"
        json_str = f"{games_str}.json"

        players_str = f"{players_tag}{x}"
        json_str = f"{players_str}.json"

        data = load_data(json_str)
        upload_to_s3(data, file_tag = games_str)
        print(f"Uploaded {games_str} successfully")

        data = load_data(json_str)
        upload_to_s3(data, file_tag = players_str)
        print(f"Uploaded {players_str} successfully")

def main():
    # fetch_dataset()
    # do_uploads()
    pass



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occured: {e}")

    