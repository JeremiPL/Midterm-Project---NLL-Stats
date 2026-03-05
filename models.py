from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy import Column, String

class Bio(SQLModel, table=True):
    player_name: str = Field(default=None, primary_key=True)
    number: int | None = None
    position: str | None = None
    team: str | None = None
    age: int | None = None
    hometown: str | None = None
    birthdate: str | None = None
    weight: str | None = None
    shoots: str | None = None


class Stats(SQLModel, table=True):
    # basic identifiers
    player_name: str = Field(default=None, foreign_key="bio.player_name", primary_key=True)
    team: str = Field(default=None, index=True)
    position: str = Field(default=None, index=True)

    # common box score statistics
    games_played: int | None = None
    goals: int | None = None
    assists: int | None = None
    points: int | None = None
    plus_minus: int | None = None
    shots_on_goal: int | None = None
    shooting_percentage: float | None = None
    loose_balls: int | None = None
    turnovers: int | None = None
    penalty_minutes: int | None = None

    # faceoff and special categories
    faceoffs_won: int | None = None
    faceoffs_lost: int | None = None
    faceoff_percentage: float | None = None

    # defensive/goalie stats (optional for non-goalies)
    saves: int | None = None
    goals_against: int | None = None
    goals_against_average: float | None = None
    wins: int | None = None


engine = create_engine("sqlite:///boxlacrosse.db")
SQLModel.metadata.create_all(engine)