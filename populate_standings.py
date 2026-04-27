"""Populate the team_standing table from data/standings-data.json."""
import json
from sqlmodel import Session
from models import TeamStanding, engine, SQLModel

# Ensure the table exists
SQLModel.metadata.create_all(engine)

with open("data/standings-data.json") as f:
    seasons = json.load(f)

with Session(engine) as session:
    for season in seasons:
        season_id = season["seasonId"]
        season_label = season["season"]
        stage = season["stage"]

        for entry in season["standings"]:
            standing = TeamStanding(
                season_id=season_id,
                season_label=season_label,
                stage=stage,
                rank=entry["rank"],
                team=entry["team"],
                wins=entry["wins"],
                losses=entry["losses"],
                games_played=entry["gamesPlayed"],
                goals_for=entry.get("goalsFor"),
                goals_against=entry.get("goalsAgainst"),
                goal_diff=entry.get("goalDiff"),
                home_record=entry.get("homeRecord"),
                road_record=entry.get("roadRecord"),
                last5=entry.get("last5"),
                streak=entry.get("streak"),
                clinched=entry.get("clinched"),
            )
            session.add(standing)

    session.commit()
    print(f"Inserted standings for {len(seasons)} season(s).")
