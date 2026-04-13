from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, create_engine, select
from models import PlayerProfile, PlayerStats, engine

app = FastAPI(title="NLL Box Lacrosse Stats")

@app.get("/api/players")
def get_players():
    """Get all players with their stats"""
    with Session(engine) as session:
        # Join player profile with stats
        stmt = select(PlayerProfile, PlayerStats).join(
            PlayerStats, PlayerProfile.player_id == PlayerStats.player_id
        )
        results = session.exec(stmt).all()
        
        players = []
        for profile, stats in results:
            players.append({
                "player_id": profile.player_id,
                "player_name": profile.player_name,
                "team": profile.team,
                "position": profile.position,
                "number": profile.number,
                "goals": stats.goals,
                "assists": stats.assists,
                "points": stats.points,
                "games_played": stats.games_played,
                "penalty_minutes": stats.penalty_minutes,
                "power_play_goals": stats.power_play_goals,
                "power_play_assists": stats.power_play_assists,
                "short_handed_goals": stats.short_handed_goals,
                "loose_balls": stats.loose_balls,
                "turnovers": stats.turnovers,
                "caused_turnovers": stats.caused_turnovers,
                "blocked_shots": stats.blocked_shots,
                "shots_on_goal": stats.shots_on_goal,
                "faceoffs_won": stats.faceoffs_won,
                "faceoffs_lost": stats.faceoffs_lost,
                "faceoff_percentage": stats.faceoff_percentage,
            })
        
        return players

@app.get("/api/players/{player_id}")
def get_player_detail(player_id: int):
    """Get detailed stats for a specific player"""
    with Session(engine) as session:
        profile = session.exec(
            select(PlayerProfile).where(PlayerProfile.player_id == player_id)
        ).first()
        
        stats = session.exec(
            select(PlayerStats).where(PlayerStats.player_id == player_id)
        ).first()
        
        if not profile or not stats:
            return {"error": "Player not found"}
        
        return {
            "profile": {
                "player_id": profile.player_id,
                "player_name": profile.player_name,
                "number": profile.number,
                "position": profile.position,
                "team": profile.team,
                "age": profile.age,
                "height": profile.height,
                "weight": profile.weight,
                "hometown": profile.hometown,
                "birthdate": profile.birthdate,
                "shoots": profile.shoots,
                "college": profile.college,
            },
            "stats": {
                "games_played": stats.games_played,
                "goals": stats.goals,
                "assists": stats.assists,
                "points": stats.points,
                "shots_on_goal": stats.shots_on_goal,
                "loose_balls": stats.loose_balls,
                "turnovers": stats.turnovers,
                "penalty_minutes": stats.penalty_minutes,
                "faceoffs_won": stats.faceoffs_won,
                "faceoffs_lost": stats.faceoffs_lost,
                "faceoff_percentage": stats.faceoff_percentage,
                "caused_turnovers": stats.caused_turnovers,
                "minutes_played": stats.minutes_played,
                "saves": stats.saves,
                "goals_against": stats.goals_against,
                "goals_against_average": stats.goals_against_average,
                "wins": stats.wins,
                "losses": stats.losses,
                "save_percentage": stats.save_percentage,
            }
        }

app.mount("/", StaticFiles(directory="static", html=True), name="static")