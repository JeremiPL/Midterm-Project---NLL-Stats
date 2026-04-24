from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, create_engine, select
from models import PlayerProfile, PlayerStats, ScheduleGame, engine

app = FastAPI(title="NLL Box Lacrosse Stats")

@app.get("/api/players")
def get_players():
    with Session(engine) as session:
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
                "season": stats.season,
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
                "minutes_played": stats.minutes_played,
                "goals_against_average": stats.goals_against_average,
                "wins": stats.wins,
                "save_percentage": stats.save_percentage,
            })
        
        return players

@app.get("/api/players/{player_id}")
def get_player_detail(player_id: int):
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


@app.get("/api/schedule")
def get_schedule(
    season_id: str = "225",
    stage: str = "REG",
    week: str = "all",
    team: str = "",
):
    with Session(engine) as session:
        stmt = select(ScheduleGame).where(
            ScheduleGame.season_id == season_id,
            ScheduleGame.stage == stage,
        )

        if week != "all":
            try:
                stmt = stmt.where(ScheduleGame.week == int(week))
            except ValueError:
                return []

        if team:
            stmt = stmt.where(
                (ScheduleGame.away_team_id == team) | (ScheduleGame.home_team_id == team)
            )

        games = session.exec(stmt).all()

        games.sort(key=lambda game: (game.week or 999, game.date))

        return [
            {
                "seasonId": game.season_id,
                "stage": game.stage,
                "week": str(game.week) if game.week is not None else "",
                "date": game.date,
                "awayTeam": game.away_team,
                "homeTeam": game.home_team,
                "awayScore": game.away_score,
                "homeScore": game.home_score,
                "result": game.final_score or (
                    f"{game.away_score} - {game.home_score}"
                    if game.away_score is not None and game.home_score is not None
                    else "TBD"
                ),
                "status": game.status,
                "venue": game.location,
                "recapLink": game.recap_link,
                "awayTeamId": game.away_team_id,
                "homeTeamId": game.home_team_id,
            }
            for game in games
        ]

app.mount("/", StaticFiles(directory="static", html=True), name="static")