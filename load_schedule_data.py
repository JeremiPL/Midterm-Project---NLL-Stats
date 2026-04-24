"""Load schedule games from static/schedule-data.json into the schedule_game table."""

import json
from sqlmodel import Session, select
from models import engine, ScheduleGame

SCHEDULE_JSON_PATH = "data/schedule-data.json"


def safe_int(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_final_score(away_score, home_score):
    if away_score is None or home_score is None:
        return None
    return f"{away_score}-{home_score}"


def load_schedule_data():
    with open(SCHEDULE_JSON_PATH, "r", encoding="utf-8") as file:
        rows = json.load(file)

    with Session(engine) as session:
        existing_rows = session.exec(select(ScheduleGame)).all()
        if existing_rows:
            print(f"Clearing {len(existing_rows)} existing schedule rows...")
            for row in existing_rows:
                session.delete(row)
            session.commit()

        print(f"Loading {len(rows)} schedule games...")

        inserted = 0
        for row in rows:
            away_score = safe_int(row.get("awayScore"))
            home_score = safe_int(row.get("homeScore"))
            week_value = safe_int(row.get("week"))

            game = ScheduleGame(
                game_id=row.get("gameId"),
                season_id=str(row.get("seasonId", "")),
                stage=str(row.get("stage", "REG")),
                week=week_value,
                date=str(row.get("date", "TBD")),
                away_team=str(row.get("awayTeam", "Unknown Team")),
                home_team=str(row.get("homeTeam", "Unknown Team")),
                location=str(row.get("venue", "N/A")),
                away_score=away_score,
                home_score=home_score,
                final_score=build_final_score(away_score, home_score),
                status=str(row.get("status", "Scheduled")),
                recap_link=row.get("recapLink"),
                away_team_id=row.get("awayTeamId"),
                home_team_id=row.get("homeTeamId"),
            )
            session.add(game)
            inserted += 1

        session.commit()
        print(f"Done. Inserted {inserted} schedule rows into schedule_game.")


if __name__ == "__main__":
    load_schedule_data()
