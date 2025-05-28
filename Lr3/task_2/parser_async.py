import asyncio
import time
import pandas as pd
from sqlmodel import select
from task_2.connection import engine, init_db, get_async_session
from task_2.models import Participant, Team
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession


def load_google_sheet_csv(url: str) -> list[dict]:
    sheet_id = url.split("/d/")[1].split("/")[0]
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(export_url)
    return df.to_dict(orient="records")


def parse_participant(row: dict) -> dict:
    return {
        "full_name": row["ФИО"],
        "nickname": row["Никнейм"],
        "email": row["E-mail"],
        "phone": "+" + str(row["Номер телефона"]),
        "skill": row["Отметьте ваш главный навык"],
        "team_name": row["Команда"],
    }


async def create_team_if_not_exists(name: str, session: AsyncSession) -> Team:
    result = await session.execute(select(Team).where(Team.name == name))
    team = result.scalars().first()
    if team is None:
        team = Team(name=name)
        session.add(team)
        await session.commit()
        await session.refresh(team)
    return team


async def create_participant_in_db(data: dict, session: AsyncSession) -> Participant:
    participant = Participant(
        full_name=data["full_name"],
        nickname=data["nickname"],
        email=data["email"],
        phone=data["phone"],
        skill=data["skill"],
    )
    try:
        session.add(participant)
        await session.commit()
        await session.refresh(participant)
    except IntegrityError:
        await session.rollback()
        result = await session.execute(
            select(Participant).where(Participant.nickname == data["nickname"])
        )
        participant = result.scalars().one()
    return participant


async def assign_participant_to_team(participant: Participant, team_id: int, session: AsyncSession):
    participant.team_id = team_id
    session.add(participant)
    await session.commit()
    await session.refresh(participant)


async def parse_and_save(data: list[dict]):
    async for session in get_async_session():
        team_cache: dict[str, int] = {}

        for row in data:
            if not row.get("Никнейм"):
                continue

            parsed = parse_participant(row)
            team_name = parsed["team_name"]

            if team_name not in team_cache:
                team = await create_team_if_not_exists(team_name, session)
                team_cache[team_name] = team.id

            participant = await create_participant_in_db(parsed, session)
            await assign_participant_to_team(participant, team_cache[team_name], session)


async def main(url: str):
    start = time.time()
    await init_db()
    # url = "https://docs.google.com/spreadsheets/d/1mQN3GROxytwL-8Y_Hi9Gxrf3XeP9Kqe7SzII6SajWSo"
    records = load_google_sheet_csv(url)
    await parse_and_save(records)
    print(f"Время выполнения: {time.time() - start:.2f} сек")