import json
import os
import sys
import boto3
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

if not all([WIKI_PASS, WIKI_USER, AWS_KEY, AWS_SECRET,AWS_REGION]):
    print("ERROR: Missing environment variables!")
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

def upload_to_s3(data, bucket_name = "lol-esports-raw-data-688600819773-eu-central-1-an"):
    if not data:
        return
    print("Connecting to AWS S3...")
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    data = json.dumps(data, indent=4)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"raw/matches_{timestamp}.json"
    print(f"Uploading to s3://{bucket_name}/{file_name}")
    s3_client.put_object(
        Bucket = bucket_name,
        Key = file_name,
        Body = data,
        ContentType = "application/json"
    )
    print("The data has landed in the cloud!")



if __name__ == "__main__":
    target_tournament = "2025 Season World Championship"

    try:
        raw_games = fetch_tournament_data(target_tournament)
        if raw_games:
            save_raw_data(raw_games)
            upload_to_s3(raw_games)
        else:
            print("No games found")
    except Exception as e:
        print(f"An error occured: {e}")

    