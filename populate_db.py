"""
Populate NLL database with realistic 2024 season player data
This script populates the database with player profiles and statistics
"""

from sqlmodel import Session, select
from models import engine, PlayerProfile, PlayerStats

# Realistic 2024 NLL player data
PLAYERS_DATA = [
    # Player 1: Toronto Rock - Forward
    {
        "profile": {
            "player_id": 1,
            "player_name": "Connor Fields",
            "number": 2,
            "position": "FORWARD",
            "team": "Toronto Rock",
            "age": 28,
            "height": "6'0\"",
            "weight": "185 lbs",
            "hometown": "Toronto, ON",
            "birthdate": "1995-08-15",
            "shoots": "Right",
            "college": "University of Toronto"
        },
        "stats": {
            "player_id": 1,
            "player_name": "Connor Fields",
            "team": "Toronto Rock",
            "position": "FORWARD",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 47,
            "assists": 35,
            "points": 82,
            "plus_minus": 8,
            "shots_on_goal": 142,
            "shooting_percentage": 33.1,
            "loose_balls": 145,
            "loose_balls_lost": 28,
            "turnovers": 8,
            "ground_balls": 156,
            "penalty_minutes": 12,
            "penalties": 4,
            "faceoffs_won": 245,
            "faceoffs_lost": 156,
            "faceoff_percentage": 61.1,
            "caused_turnovers": 18,
            "defensive_ground_balls": 42,
        }
    },
    # Player 2: Buffalo Bandits - Forward
    {
        "profile": {
            "player_id": 2,
            "player_name": "Dan Dawson",
            "number": 30,
            "position": "FORWARD",
            "team": "Buffalo Bandits",
            "age": 34,
            "height": "6'1\"",
            "weight": "190 lbs",
            "hometown": "Buffalo, NY",
            "birthdate": "1989-03-22",
            "shoots": "Right",
            "college": "Syracuse University"
        },
        "stats": {
            "player_id": 2,
            "player_name": "Dan Dawson",
            "team": "Buffalo Bandits",
            "position": "FORWARD",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 56,
            "assists": 42,
            "points": 98,
            "plus_minus": 12,
            "shots_on_goal": 168,
            "shooting_percentage": 33.3,
            "loose_balls": 156,
            "loose_balls_lost": 32,
            "turnovers": 12,
            "ground_balls": 178,
            "penalty_minutes": 14,
            "penalties": 5,
            "faceoffs_won": 268,
            "faceoffs_lost": 142,
            "faceoff_percentage": 65.4,
            "caused_turnovers": 22,
            "defensive_ground_balls": 48,
        }
    },
    # Player 3: Toronto Rock - Transition
    {
        "profile": {
            "player_id": 3,
            "player_name": "Kyle Killen",
            "number": 17,
            "position": "TRANSITION",
            "team": "Toronto Rock",
            "age": 32,
            "height": "5'11\"",
            "weight": "175 lbs",
            "hometown": "Markham, ON",
            "birthdate": "1991-07-10",
            "shoots": "Left",
            "college": "Limestone University"
        },
        "stats": {
            "player_id": 3,
            "player_name": "Kyle Killen",
            "team": "Toronto Rock",
            "position": "TRANSITION",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 28,
            "assists": 52,
            "points": 80,
            "plus_minus": 5,
            "shots_on_goal": 98,
            "shooting_percentage": 28.6,
            "loose_balls": 267,
            "loose_balls_lost": 45,
            "turnovers": 18,
            "ground_balls": 298,
            "penalty_minutes": 22,
            "penalties": 8,
            "faceoffs_won": 156,
            "faceoffs_lost": 124,
            "faceoff_percentage": 55.7,
            "caused_turnovers": 28,
            "defensive_ground_balls": 156,
        }
    },
    # Player 4: Toronto Rock - Defence
    {
        "profile": {
            "player_id": 4,
            "player_name": "Challen Rogers",
            "number": 1,
            "position": "DEFENCE",
            "team": "Toronto Rock",
            "age": 36,
            "height": "6'2\"",
            "weight": "195 lbs",
            "hometown": "Ajax, ON",
            "birthdate": "1987-11-05",
            "shoots": "Right",
            "college": "University of Guelph"
        },
        "stats": {
            "player_id": 4,
            "player_name": "Challen Rogers",
            "team": "Toronto Rock",
            "position": "DEFENCE",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 8,
            "assists": 16,
            "points": 24,
            "plus_minus": -3,
            "shots_on_goal": 32,
            "shooting_percentage": 25.0,
            "loose_balls": 289,
            "loose_balls_lost": 38,
            "turnovers": 42,
            "ground_balls": 312,
            "penalty_minutes": 58,
            "penalties": 18,
            "faceoffs_won": 0,
            "faceoffs_lost": 0,
            "faceoff_percentage": 0.0,
            "caused_turnovers": 32,
            "defensive_ground_balls": 278,
        }
    },
    # Player 5: Buffalo Bandits - Goaltender
    {
        "profile": {
            "player_id": 5,
            "player_name": "Cody Jamieson",
            "number": 25,
            "position": "GOALTENDER",
            "team": "Buffalo Bandits",
            "age": 31,
            "height": "6'1\"",
            "weight": "185 lbs",
            "hometown": "Fort Erie, ON",
            "birthdate": "1992-05-18",
            "shoots": "Left",
            "college": "Brock University"
        },
        "stats": {
            "player_id": 5,
            "player_name": "Cody Jamieson",
            "team": "Buffalo Bandits",
            "position": "GOALTENDER",
            "season": 2024,
            "games_played": 14,
            "games_started": 14,
            "goals": 0,
            "assists": 0,
            "points": 0,
            "plus_minus": 0,
            "shots_on_goal": 0,
            "shooting_percentage": 0.0,
            "loose_balls": 0,
            "loose_balls_lost": 0,
            "turnovers": 0,
            "ground_balls": 0,
            "penalty_minutes": 0,
            "penalties": 0,
            "faceoffs_won": None,
            "faceoffs_lost": None,
            "faceoff_percentage": None,
            "caused_turnovers": None,
            "defensive_ground_balls": None,
            "saves": 385,
            "goals_against": 108,
            "goals_against_average": 7.7,
            "wins": 8,
            "losses": 6,
            "save_percentage": 78.1,
        }
    },
    # Player 6: Buffalo Bandits - Forward
    {
        "profile": {
            "player_id": 6,
            "player_name": "Dhane Smith",
            "number": 10,
            "position": "FORWARD",
            "team": "Buffalo Bandits",
            "age": 29,
            "height": "6'0\"",
            "weight": "182 lbs",
            "hometown": "Whitby, ON",
            "birthdate": "1994-12-03",
            "shoots": "Right",
            "college": "York University"
        },
        "stats": {
            "player_id": 6,
            "player_name": "Dhane Smith",
            "team": "Buffalo Bandits",
            "position": "FORWARD",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 52,
            "assists": 38,
            "points": 90,
            "plus_minus": 10,
            "shots_on_goal": 156,
            "shooting_percentage": 33.3,
            "loose_balls": 134,
            "loose_balls_lost": 26,
            "turnovers": 6,
            "ground_balls": 152,
            "penalty_minutes": 10,
            "penalties": 3,
            "faceoffs_won": 234,
            "faceoffs_lost": 168,
            "faceoff_percentage": 58.2,
            "caused_turnovers": 16,
            "defensive_ground_balls": 38,
        }
    },
    # Player 7: Buffalo Bandits - Transition
    {
        "profile": {
            "player_id": 7,
            "player_name": "Mark Steenhuis",
            "number": 24,
            "position": "TRANSITION",
            "team": "Buffalo Bandits",
            "age": 33,
            "height": "5'10\"",
            "weight": "188 lbs",
            "hometown": "St. Catharines, ON",
            "birthdate": "1990-09-14",
            "shoots": "Right",
            "college": "McMaster University"
        },
        "stats": {
            "player_id": 7,
            "player_name": "Mark Steenhuis",
            "team": "Buffalo Bandits",
            "position": "TRANSITION",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 32,
            "assists": 48,
            "points": 80,
            "plus_minus": 2,
            "shots_on_goal": 104,
            "shooting_percentage": 30.8,
            "loose_balls": 256,
            "loose_balls_lost": 42,
            "turnovers": 14,
            "ground_balls": 278,
            "penalty_minutes": 18,
            "penalties": 6,
            "faceoffs_won": 168,
            "faceoffs_lost": 142,
            "faceoff_percentage": 54.2,
            "caused_turnovers": 24,
            "defensive_ground_balls": 142,
        }
    },
    # Player 8: Toronto Rock - Defence
    {
        "profile": {
            "player_id": 8,
            "player_name": "Ryan Dilks",
            "number": 23,
            "position": "DEFENCE",
            "team": "Toronto Rock",
            "age": 35,
            "height": "6'3\"",
            "weight": "192 lbs",
            "hometown": "Whitby, ON",
            "birthdate": "1988-06-20",
            "shoots": "Right",
            "college": "University of Ontario"
        },
        "stats": {
            "player_id": 8,
            "player_name": "Ryan Dilks",
            "team": "Toronto Rock",
            "position": "DEFENCE",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 6,
            "assists": 14,
            "points": 20,
            "plus_minus": -1,
            "shots_on_goal": 28,
            "shooting_percentage": 21.4,
            "loose_balls": 312,
            "loose_balls_lost": 52,
            "turnovers": 58,
            "ground_balls": 334,
            "penalty_minutes": 62,
            "penalties": 20,
            "faceoffs_won": 0,
            "faceoffs_lost": 0,
            "faceoff_percentage": 0.0,
            "caused_turnovers": 28,
            "defensive_ground_balls": 298,
        }
    },
    # Player 9: Toronto Rock - Forward
    {
        "profile": {
            "player_id": 9,
            "player_name": "Charlotte Muller",
            "number": 11,
            "position": "FORWARD",
            "team": "Toronto Rock",
            "age": 26,
            "height": "5'8\"",
            "weight": "168 lbs",
            "hometown": "Vancouver, BC",
            "birthdate": "1997-04-08",
            "shoots": "Left",
            "college": "University of British Columbia"
        },
        "stats": {
            "player_id": 9,
            "player_name": "Charlotte Muller",
            "team": "Toronto Rock",
            "position": "FORWARD",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 44,
            "assists": 38,
            "points": 82,
            "plus_minus": 7,
            "shots_on_goal": 138,
            "shooting_percentage": 31.9,
            "loose_balls": 128,
            "loose_balls_lost": 24,
            "turnovers": 4,
            "ground_balls": 138,
            "penalty_minutes": 8,
            "penalties": 2,
            "faceoffs_won": 212,
            "faceoffs_lost": 168,
            "faceoff_percentage": 55.8,
            "caused_turnovers": 14,
            "defensive_ground_balls": 32,
        }
    },
    # Player 10: Toronto Rock - Transition
    {
        "profile": {
            "player_id": 10,
            "player_name": "Corey Small",
            "number": 4,
            "position": "TRANSITION",
            "team": "Toronto Rock",
            "age": 37,
            "height": "5'9\"",
            "weight": "180 lbs",
            "hometown": "Stouffville, ON",
            "birthdate": "1986-10-12",
            "shoots": "Right",
            "college": "Durham College"
        },
        "stats": {
            "player_id": 10,
            "player_name": "Corey Small",
            "team": "Toronto Rock",
            "position": "TRANSITION",
            "season": 2024,
            "games_played": 18,
            "games_started": 18,
            "goals": 35,
            "assists": 46,
            "points": 81,
            "plus_minus": 6,
            "shots_on_goal": 112,
            "shooting_percentage": 31.3,
            "loose_balls": 298,
            "loose_balls_lost": 48,
            "turnovers": 22,
            "ground_balls": 324,
            "penalty_minutes": 26,
            "penalties": 9,
            "faceoffs_won": 142,
            "faceoffs_lost": 138,
            "faceoff_percentage": 50.7,
            "caused_turnovers": 32,
            "defensive_ground_balls": 168,
        }
    },
]


def populate_database():
    """Insert sample NLL player data into the database"""
    try:
        with Session(engine) as session:
            # Check if data already exists
            existing_players = session.exec(select(PlayerProfile)).all()
            if len(existing_players) > 0:
                print(f"Database already contains {len(existing_players)} players.")
                response = input("Do you want to clear and reload? (yes/no): ")
                if response.lower() != "yes":
                    print("Skipping population.")
                    return
                # Clear existing data
                for stats in session.exec(select(PlayerStats)).all():
                    session.delete(stats)
                for profile in session.exec(select(PlayerProfile)).all():
                    session.delete(profile)
                session.commit()
                print("Cleared existing data.")
            
            # Insert players
            for player_data in PLAYERS_DATA:
                # Create profile
                profile = PlayerProfile(**player_data["profile"])
                session.add(profile)
                
            session.commit()
            print(f"✓ Inserted {len(PLAYERS_DATA)} player profiles")
            
            # Insert stats
            for player_data in PLAYERS_DATA:
                stats = PlayerStats(**player_data["stats"])
                session.add(stats)
            
            session.commit()
            print(f"✓ Inserted {len(PLAYERS_DATA)} player statistics")
            
        print("\n✓ Database populated successfully!")
        
    except Exception as e:
        print(f"✗ Error populating database: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("NLL Player Database Population Script")
    print("=" * 60)
    populate_database()
