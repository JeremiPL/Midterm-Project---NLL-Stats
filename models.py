from sqlmodel import SQLModel, Field, create_engine
from datetime import date
from typing import Optional

class PlayerProfile(SQLModel, table=True):
    """Player biographical and personal information"""
    __tablename__ = "player_profile"
    
    player_id: int = Field(default=None, primary_key=True)
    player_name: str = Field(index=True)
    number: Optional[int] = None
    position: str = Field(index=True)  # FORWARD, TRANSITION, DEFENCE, GOALTENDER
    team: str = Field(index=True)
    
    # Personal Information
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    hometown: Optional[str] = None
    birthdate: Optional[str] = None
    
    # Playing Details
    shoots: Optional[str] = None
    drafted: Optional[str] = None
    college: Optional[str] = None


class PlayerStats(SQLModel, table=True):
    """Player season statistics - 2025-2026 season"""
    __tablename__ = "player_stats"
    
    stat_id: int = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player_profile.player_id", index=True)
    player_name: str = Field(index=True)
    team: str = Field(index=True)
    position: str = Field(index=True)
    season: int = 2026  # 2025-2026 season
    
    # Game Statistics
    games_played: Optional[int] = None
    
    # Scoring Statistics
    goals: Optional[int] = None
    assists: Optional[int] = None
    points: Optional[int] = None
    
    # Shot Statistics
    shots_on_goal: Optional[int] = None
    
    # Possession & Turnovers
    loose_balls: Optional[int] = None
    turnovers: Optional[int] = None
    
    # Penalties & Discipline
    penalty_minutes: Optional[int] = None
    power_play_goals: Optional[int] = None
    power_play_assists: Optional[int] = None
    short_handed_goals: Optional[int] = None
    
    # Faceoff Statistics (primarily for FORWARD/TRANSITION positions)
    faceoffs_won: Optional[int] = None
    faceoffs_lost: Optional[int] = None
    faceoff_percentage: Optional[float] = None
    
    # Defensive Statistics
    caused_turnovers: Optional[int] = None
    blocked_shots: Optional[int] = None
    
    # Goalie Statistics (primarily for GOALTENDER position)
    minutes_played: Optional[str] = None
    saves: Optional[int] = None
    goals_against: Optional[int] = None
    goals_against_average: Optional[float] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    save_percentage: Optional[float] = None


engine = create_engine("sqlite:///boxlacrosse.db")
SQLModel.metadata.create_all(engine)