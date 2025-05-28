import time
import gspread
from google.oauth2.service_account import Credentials
import requests


def init_google_sheet(url, creds_path="creds.json"):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(url)
    return sh


def get_teams():
    response = requests.get("http://localhost:8000/teams/")
    return response.json()


def get_participants():
    response = requests.get("http://localhost:8000/participants/")
    return response.json()


def create_team(team_name):
    response = requests.post("http://localhost:8000/teams/", json={"name": team_name})
    if response.status_code != 200:
        print("Failed to create team:", response.status_code, response.json())
    return response.json()


def parse_participant(row):
    return {
        "full_name": row["ФИО"],
        "nickname": row["Никнейм"],
        "email": row["E-mail"],
        "phone": "+" + str(row["Номер телефона"]),
        "skill": row["Отметьте ваш главный навык"],
        "team_name": row["Команда"],
    }


def create_participant(row):
    data = parse_participant(row)
    response = requests.post("http://localhost:8000/participants/", json=data)
    if response.status_code != 200:
        print("Failed to create participant:", response.status_code, response.json())
    return response.json()


def add_participant_to_team(team_id, participant_id):
    response = requests.patch(
        f"http://localhost:8000/teams/{team_id}/participants/",
        params={"participant_id": participant_id}
    )
    if response.status_code != 200:
        print("Failed to add to team:", response.status_code, response.json())
    return response.json()


if __name__ == "__main__":
    start_time = time.time()

    url = "https://docs.google.com/spreadsheets/d/1mQN3GROxytwL-8Y_Hi9Gxrf3XeP9Kqe7SzII6SajWSo"
    sh = init_google_sheet(url)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()

    existing_teams = get_teams()
    team_names = set(row["Команда"] for row in data if row.get("Команда"))
    for team_name in team_names:
        if team_name not in [team["name"] for team in existing_teams]:
            create_team(team_name)

    teams = get_teams()
    team_mapping = {team["name"]: team["id"] for team in teams}

    for row in data:
        if row.get("Никнейм"):
            create_participant(row)

    participants = get_participants()
    participants_mapping = {
        participant["nickname"]: participant["id"]
        for participant in participants
    }

    for row in data:
        if row.get("Команда") and row.get("Никнейм") in participants_mapping:
            add_participant_to_team(
                team_mapping[row["Команда"]],
                participants_mapping[row["Никнейм"]],
            )

    print(f"Общее время выполнения: {time.time() - start_time:.2f} секунд.")
