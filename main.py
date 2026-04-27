import json
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, create_engine, select
from models import PlayerProfile, PlayerStats, ScheduleGame, TeamStanding, engine


TEAM_LOGOS = {
    "oshawa firewolves": "Oshawa_FireWolves Logo.png",
    "buffalo bandits": "Buffalo_Bandits_logo.svg.png",
    "san diego seals": "San_Diego_Seals_primary_logo.png",
    "colorado mammoth": "Colorado mammoth logo.svg",
    "georgia swarm": "Georgia Swarm Logo.webp",
    "vancouver warriors": "Vancouver_Warriors_Logo.png",
    "calgary roughnecks": "Calgary_Roughnecks_logo.svg.png",
    "toronto rock": "Toronto_Rock_logo.svg.png",
    "saskatchewan rush": "Saskatchewan_Rush_logo.png",
    "las vegas desert dogs": "Las_Vegas_Desert_Dogs logo.png",
    "philadelphia wings": "Philadelphia_Wings logo.png",
    "halifax thunderbirds": "Halifax_Thunderbirds_logo.png",
    "rochester knighthawks": "Rochester_Knighthawks_logo.png",
    "ottawa black bears": "Ottawa Black Bears logo.png",
    "albany firewolves": "Oshawa_FireWolves Logo.png",
}

DEFAULT_TEAM_LOGO = "team-logos/default-logo.svg"

SEASON_225_REG_ORDER = [
    "Vancouver Warriors",
    "Colorado Mammoth",
    "Saskatchewan Rush",
    "Georgia Swarm",
    "Buffalo Bandits",
    "Toronto Rock",
    "San Diego Seals",
    "Halifax Thunderbirds",
    "Las Vegas Desert Dogs",
    "Ottawa Black Bears",
    "Calgary Roughnecks",
    "Rochester Knighthawks",
    "Oshawa FireWolves",
    "Philadelphia Wings",
]

SEASON_224_REG_ORDER = [
    "Buffalo Bandits",
    "Saskatchewan Rush",
    "Halifax Thunderbirds",
    "Vancouver Warriors",
    "Rochester Knighthawks",
    "Calgary Roughnecks",
    "Georgia Swarm",
    "San Diego Seals",
    "Ottawa Black Bears",
    "Colorado Mammoth",
    "Albany FireWolves",
    "Philadelphia Wings",
    "Toronto Rock",
    "Las Vegas Desert Dogs",
]

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


@app.get("/api/standings")
def get_standings(
    season_id: str = "225",
    stage: str = "REG",
):
    # Return pre-computed historical standings from DB if no schedule games exist
    historical_rows = None
    with Session(engine) as session:
        db_standings = session.exec(
            select(TeamStanding).where(
                TeamStanding.season_id == season_id,
                TeamStanding.stage == stage,
            ).order_by(TeamStanding.rank)
        ).all()
        if db_standings:
            historical_rows = db_standings

    with Session(engine) as session:
        games = session.exec(
            select(ScheduleGame).where(
                ScheduleGame.season_id == season_id,
                ScheduleGame.stage == stage,
            )
        ).all()

    # Fall back to DB historical standings when no schedule games exist
    if not games and historical_rows:
        rows = []
        for entry in historical_rows:
            logo = TEAM_LOGOS.get(entry.team.lower())
            rows.append({
                "rank": entry.rank,
                "team": entry.team,
                "logo": f"team-logos/{logo}" if logo else DEFAULT_TEAM_LOGO,
                "wins": entry.wins,
                "losses": entry.losses,
                "gamesPlayed": entry.games_played,
                "goalsFor": entry.goals_for,
                "goalsAgainst": entry.goals_against,
                "goalDiff": entry.goal_diff,
                "homeRecord": entry.home_record,
                "roadRecord": entry.road_record,
                "last5": entry.last5,
                "streak": entry.streak,
                "clinched": entry.clinched,
                "record": f"{entry.wins}-{entry.losses}",
            })
        return {
            "seasonId": season_id,
            "stage": stage,
            "standings": rows,
            "source": "historical",
        }



    standings = {}
    for game in games:
        away_team = game.away_team
        home_team = game.home_team

        if not away_team or not home_team:
            continue

        if away_team not in standings:
            away_logo = TEAM_LOGOS.get(away_team.lower())
            standings[away_team] = {
                "teamId": game.away_team_id,
                "team": away_team,
                "logo": f"team-logos/{away_logo}" if away_logo else DEFAULT_TEAM_LOGO,
                "wins": 0,
                "losses": 0,
                "gamesPlayed": 0,
            }

        if home_team not in standings:
            home_logo = TEAM_LOGOS.get(home_team.lower())
            standings[home_team] = {
                "teamId": game.home_team_id,
                "team": home_team,
                "logo": f"team-logos/{home_logo}" if home_logo else DEFAULT_TEAM_LOGO,
                "wins": 0,
                "losses": 0,
                "gamesPlayed": 0,
            }

        if not standings[away_team]["teamId"] and game.away_team_id:
            standings[away_team]["teamId"] = game.away_team_id
        if not standings[home_team]["teamId"] and game.home_team_id:
            standings[home_team]["teamId"] = game.home_team_id

        # Standings count only games that have final scores.
        if game.away_score is None or game.home_score is None:
            continue

        away = standings[away_team]
        home = standings[home_team]

        away["gamesPlayed"] += 1
        home["gamesPlayed"] += 1

        if game.away_score > game.home_score:
            away["wins"] += 1
            home["losses"] += 1
        elif game.home_score > game.away_score:
            home["wins"] += 1
            away["losses"] += 1

    rows = []
    for row in standings.values():
        row["record"] = f"{row['wins']}-{row['losses']}"
        rows.append(row)

    if season_id == "225" and stage == "REG":
        order_map = {team_name: index for index, team_name in enumerate(SEASON_225_REG_ORDER)}
        rows.sort(key=lambda row: order_map.get(row["team"], len(SEASON_225_REG_ORDER)))
    elif season_id == "224" and stage == "REG":
        order_map = {team_name: index for index, team_name in enumerate(SEASON_224_REG_ORDER)}
        rows.sort(key=lambda row: order_map.get(row["team"], len(SEASON_224_REG_ORDER)))
    else:
        rows.sort(
            key=lambda row: (
                -row["wins"],
                row["losses"],
                row["team"],
            )
        )

    for index, row in enumerate(rows, start=1):
        row["rank"] = index

    return {
        "seasonId": season_id,
        "stage": stage,
        "standings": rows,
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")