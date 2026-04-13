"""
Load 353 real 2025-2026 NLL players into the database
"""

import pickle
from sqlmodel import Session, select
from models import engine, PlayerProfile, PlayerStats

def position_map(pos_str):
    """Map position string from web to database format"""
    pos_lower = pos_str.lower().strip()
    if pos_lower in ['forward', 'f']:
        return 'FORWARD'
    elif pos_lower in ['transition', 'm', 'midfield']:
        return 'TRANSITION'
    elif pos_lower in ['defense', 'defence', 'd']:
        return 'DEFENCE'
    elif pos_lower in ['goalie', 'goaltender', 'g']:
        return 'GOALTENDER'
    return pos_str.upper()

def safe_int(val):
    """Safely convert string to int"""
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        val = val.strip().replace(',', '')
        if val and val != '-':
            try:
                return int(val)
            except:
                return None
    return None

def safe_float(val):
    """Safely convert string to float"""
    if isinstance(val, float):
        return val
    if isinstance(val, str):
        val = val.strip().replace('%', '').replace(',', '')
        if val and val != '-':
            try:
                return float(val)
            except:
                return None
    return None

def load_players():
    """Load all 353 players from pickled data"""
    
    try:
        # Load pickled player data
        with open('/tmp/nll_players_2026.pkl', 'rb') as f:
            players_data = pickle.load(f)
        
        print(f"Loaded {len(players_data)} players from source data\n")
        
        with Session(engine) as session:
            # Check if data already exists
            existing = session.exec(select(PlayerProfile)).all()
            if len(existing) > 0:
                print(f"Database already contains {len(existing)} players.")
                response = input("Clear and reload? (yes/no): ")
                if response.lower() != "yes":
                    print("Skipping load.")
                    return
                
                # Clear existing data
                for stat in session.exec(select(PlayerStats)).all():
                    session.delete(stat)
                for profile in session.exec(select(PlayerProfile)).all():
                    session.delete(profile)
                session.commit()
                print("Cleared existing data.\n")
            
            # Load players
            print("Loading player profiles and statistics...")
            player_id = 1
            
            for idx, player_data in enumerate(players_data, 1):
                try:
                    # Create profile
                    profile = PlayerProfile(
                        player_id=player_id,
                        player_name=player_data['name'],
                        position=position_map(player_data['position']),
                        team=player_data['team'],
                    )
                    session.add(profile)
                    
                    # Create stats
                    stats = PlayerStats(
                        player_id=player_id,
                        player_name=player_data['name'],
                        team=player_data['team'],
                        position=position_map(player_data['position']),
                        season=2026,
                        
                        # Basic stats
                        games_played=safe_int(player_data.get('games_played')),
                        goals=safe_int(player_data.get('goals')),
                        assists=safe_int(player_data.get('assists')),
                        points=safe_int(player_data.get('points')),
                        
                        # Shooting stats
                        shots_on_goal=safe_int(player_data.get('shots_on_goal')),
                        
                        # Possession stats
                        loose_balls=safe_int(player_data.get('loose_balls')),
                        turnovers=safe_int(player_data.get('turnovers')),
                        caused_turnovers=safe_int(player_data.get('caused_turnovers')),
                        blocked_shots=safe_int(player_data.get('blocked_shots')),
                        
                        # Penalties
                        penalty_minutes=safe_int(player_data.get('pim')),
                        power_play_goals=safe_int(player_data.get('ppg')),
                        power_play_assists=safe_int(player_data.get('ppa')),
                        short_handed_goals=safe_int(player_data.get('shg')),
                        
                        # Faceoff stats (if available)
                        faceoffs_won=None if 'faceoffs' not in player_data or player_data['faceoffs'] == '0/0' else None,
                        faceoff_percentage=safe_float(player_data.get('faceoff_pct')),
                    )
                    session.add(stats)
                    
                    if idx % 50 == 0:
                        print(f"  Processing {idx}/{len(players_data)}...")
                    
                    player_id += 1
                    
                except Exception as e:
                    print(f"  Error processing player {idx}: {e}")
                    continue
            
            session.commit()
            
            total_profiles = session.exec(select(PlayerProfile)).all()
            total_stats = session.exec(select(PlayerStats)).all()
            
            print(f"\n✓ Loaded {len(total_profiles)} player profiles")
            print(f"✓ Loaded {len(total_stats)} player statistics")
            
            # Show stats by position
            print(f"\n📊 Position breakdown in database:")
            for position in ['FORWARD', 'TRANSITION', 'DEFENCE', 'GOALTENDER']:
                count = len([p for p in total_profiles if p.position == position])
                print(f"  {position}: {count}")
            
            # Show top scorers
            print(f"\n🏆 Top 10 scorers (2025-2026):")
            sorted_stats = sorted(total_stats, key=lambda x: x.points or 0, reverse=True)
            for i, stat in enumerate(sorted_stats[:10], 1):
                print(f"  {i:2}. {stat.player_name:<20} {stat.team:<25} {stat.position:<10} {stat.points} pts")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("NLL PLAYER DATABASE LOADER - 2025-2026 SEASON")
    print("=" * 70 + "\n")
    
    success = load_players()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ DATABASE LOADED SUCCESSFULLY!")
        print("=" * 70)
    else:
        print("\n✗ Loading failed!")
