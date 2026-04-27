from sqlmodel import SQLModel, Field, create_engine
from typing import Optional

class PlayerProfile(SQLModel, table=True):
    __tablename__ = "player_profile"
    
    player_id: int = Field(default=None, primary_key=True)
    player_name: str = Field(index=True)
    number: Optional[int] = None
    position: str = Field(index=True)  # FORWARD, TRANSITION, DEFENCE, GOALTENDER
    team: str = Field(index=True)
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    hometown: Optional[str] = None
    birthdate: Optional[str] = None
    shoots: Optional[str] = None
    drafted: Optional[str] = None
    college: Optional[str] = None


class PlayerStats(SQLModel, table=True):
    __tablename__ = "player_stats"
    
    stat_id: int = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player_profile.player_id", index=True)
    player_name: str = Field(index=True)
    team: str = Field(index=True)
    position: str = Field(index=True)
    season: int = 2026
    games_played: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    points: Optional[int] = None
    shots_on_goal: Optional[int] = None
    loose_balls: Optional[int] = None
    turnovers: Optional[int] = None
    penalty_minutes: Optional[int] = None
    power_play_goals: Optional[int] = None
    power_play_assists: Optional[int] = None
    short_handed_goals: Optional[int] = None
    faceoffs_won: Optional[int] = None
    faceoffs_lost: Optional[int] = None
    faceoff_percentage: Optional[float] = None
    caused_turnovers: Optional[int] = None
    blocked_shots: Optional[int] = None
    minutes_played: Optional[str] = None
    saves: Optional[int] = None
    goals_against: Optional[int] = None
    goals_against_average: Optional[float] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    save_percentage: Optional[float] = None


class TeamStanding(SQLModel, table=True):
    __tablename__ = "team_standing"

    standing_id: Optional[int] = Field(default=None, primary_key=True)
    season_id: str = Field(index=True)       # e.g. "225"
    season_label: str = Field(index=True)    # e.g. "2024-25"
    stage: str = Field(index=True)           # REG or PO
    rank: int
    team: str = Field(index=True)
    wins: int
    losses: int
    games_played: int
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    goal_diff: Optional[int] = None
    home_record: Optional[str] = None
    road_record: Optional[str] = None
    last5: Optional[str] = None
    streak: Optional[str] = None
    clinched: Optional[str] = None


class ScheduleGame(SQLModel, table=True):
    __tablename__ = "schedule_game"

    schedule_id: Optional[int] = Field(default=None, primary_key=True)
    game_id: Optional[str] = Field(default=None, index=True)

    season_id: str = Field(index=True)
    stage: str = Field(index=True)  # REG or PO
    week: Optional[int] = Field(default=None, index=True)

    date: str = Field(index=True)
    away_team: str = Field(index=True)
    home_team: str = Field(index=True)
    location: str

    away_score: Optional[int] = None
    home_score: Optional[int] = None
    final_score: Optional[str] = None

    status: Optional[str] = Field(default="Scheduled", index=True)
    recap_link: Optional[str] = None
    away_team_id: Optional[str] = Field(default=None, index=True)
    home_team_id: Optional[str] = Field(default=None, index=True)


engine = create_engine("sqlite:///boxlacrosse.db")
SQLModel.metadata.create_all(engine)