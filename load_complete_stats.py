"""Load complete NLL stats from the scraped pickle file"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from models import engine, PlayerProfile, PlayerStats


def safe_int(value):
    """Convert a value to int when possible."""
    if value is None:
        return None
    value_str = str(value).strip()
    if value_str == "" or value_str == "-":
        return None
    return int(float(value_str))


def safe_float(value):
    """Convert a value to float when possible."""
    if value is None:
        return None
    value_str = str(value).strip().replace("%", "")
    if value_str == "" or value_str == "-":
        return None
    return float(value_str)


def normalize_key(text):
    """Normalize strings for resilient matching between data sources."""
    return "".join(ch.lower() for ch in str(text or "") if ch.isalnum())


def normalize_name_loose(text):
    """Normalize player names while ignoring single-letter middle initials."""
    tokens = []
    for token in str(text or "").replace(".", " ").split():
        cleaned = "".join(ch.lower() for ch in token if ch.isalnum())
        if cleaned and len(cleaned) > 1:
            tokens.append(cleaned)
    return "".join(tokens)


def extract_profile_links():
    """Extract all player profile links from the public stats page."""
    response = requests.get(
        "https://www.nll.com/stats/all-player-stats/",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    urls = []
    seen = set()
    for anchor in soup.select("table#all_player_stats tbody td.player a"):
        href = anchor.get("href")
        if not href or not href.startswith("/players/"):
            continue
        full_url = f"https://www.nll.com{href}"
        if full_url in seen:
            continue
        seen.add(full_url)
        urls.append(full_url)
    return urls


def fetch_directory_player_numbers():
    """Fetch jersey numbers from the public NLL player directory page."""
    response = requests.get(
        "https://www.nll.com/players/",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    players = []
    for row in soup.select("table tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        name_link = cells[0].find("a")
        if not name_link:
            continue

        players.append(
            {
                "player_name": name_link.get_text(" ", strip=True),
                "number": safe_int(cells[2].get_text(" ", strip=True)),
            }
        )

    return players


def scrape_player_profile(profile_url):
    """Scrape player profile information from an individual NLL player page."""
    response = requests.get(profile_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.select_one(".player_info_section")
    if not section:
        return None

    title_map = {}
    for wrap in section.select(".stat_wrap"):
        title_el = wrap.select_one(".title")
        stat_el = wrap.select_one(".stat")
        if not title_el or not stat_el:
            continue
        key = normalize_key(title_el.get_text(" ", strip=True).replace(":", ""))
        title_map[key] = stat_el.get_text(" ", strip=True)

    name_el = section.select_one("h1")
    number_el = section.select_one(".player_number")
    position_el = section.select_one(".num_pos_team .position")
    team_el = section.select_one(".num_pos_team .team")

    return {
        "player_name": name_el.get_text(" ", strip=True) if name_el else None,
        "number": safe_int(number_el.get_text(strip=True).replace("#", "")) if number_el else None,
        "position": position_map(position_el.get_text(" ", strip=True)) if position_el else None,
        "team": team_el.get_text(" ", strip=True) if team_el else None,
        "age": safe_int(title_map.get("age")),
        "height": title_map.get("height"),
        "weight": title_map.get("weight"),
        "hometown": title_map.get("hometown"),
        "birthdate": title_map.get("birthdate"),
        "shoots": title_map.get("shoots") or title_map.get("catches"),
        "drafted": title_map.get("drafted"),
        "college": title_map.get("college"),
    }


def apply_player_profiles(session):
    """Backfill the player_profile table from individual NLL player pages."""
    profile_urls = extract_profile_links()
    if not profile_urls:
        print("\n⚠ No player profile URLs found.")
        return

    print(f"\nApplying player profile data for {len(profile_urls)} players...")

    profile_rows = session.exec(select(PlayerProfile)).all()
    profile_by_name = {normalize_key(profile.player_name): profile for profile in profile_rows}
    profile_by_name_loose = {normalize_name_loose(profile.player_name): profile for profile in profile_rows}

    updated = 0
    completed = 0
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_map = {executor.submit(scrape_player_profile, profile_url): profile_url for profile_url in profile_urls}

        for future in as_completed(future_map):
            completed += 1
            try:
                scraped = future.result()
            except Exception:
                scraped = None

            if scraped and scraped.get("player_name"):
                profile = profile_by_name.get(normalize_key(scraped["player_name"]))
                if profile is None:
                    profile = profile_by_name_loose.get(normalize_name_loose(scraped["player_name"]))
                if profile is not None:
                    profile.number = scraped["number"]
                    if scraped.get("position"):
                        profile.position = scraped["position"]
                    if scraped.get("team"):
                        profile.team = scraped["team"]
                    profile.age = scraped["age"]
                    profile.height = scraped["height"]
                    profile.weight = scraped["weight"]
                    profile.hometown = scraped["hometown"]
                    profile.birthdate = scraped["birthdate"]
                    profile.shoots = scraped["shoots"]
                    profile.drafted = scraped["drafted"]
                    profile.college = scraped["college"]
                    session.add(profile)
                    updated += 1

            if completed % 50 == 0:
                session.commit()
                print(f"  ✓ Scraped {completed} profile pages...")

    session.commit()
    print(f"✓ Updated profile fields for {updated} players")


def apply_directory_numbers(session):
    """Fill any remaining missing jersey numbers from the NLL player directory."""
    directory_rows = fetch_directory_player_numbers()
    if not directory_rows:
        print("\n⚠ No directory jersey rows found.")
        return

    print(f"\nApplying directory jersey numbers for {len(directory_rows)} players...")

    profile_rows = session.exec(select(PlayerProfile)).all()
    profile_by_name = {normalize_key(profile.player_name): profile for profile in profile_rows}
    profile_by_name_loose = {normalize_name_loose(profile.player_name): profile for profile in profile_rows}

    updated = 0
    for row in directory_rows:
        if row["number"] is None:
            continue

        profile = profile_by_name.get(normalize_key(row["player_name"]))
        if profile is None:
            profile = profile_by_name_loose.get(normalize_name_loose(row["player_name"]))
        if profile is None or profile.number is not None:
            continue

        profile.number = row["number"]
        session.add(profile)
        updated += 1

    session.commit()
    print(f"✓ Filled {updated} missing jersey numbers from directory")

def position_map(pos):
    """Map position strings to database format"""
    pos_lower = str(pos).lower().strip()
    if pos_lower in ['f', 'forward']:
        return 'FORWARD'
    elif pos_lower in ['t', 'transition', 'm', 'midfield']:
        return 'TRANSITION'
    elif pos_lower in ['d', 'defense', 'defence']:
        return 'DEFENCE'
    elif pos_lower in ['g', 'goalie', 'goaltender']:
        return 'GOALTENDER'
    return 'TRANSITION'  # Default


def fetch_goalie_stats():
    """Fetch goalie-only stats from the same AJAX endpoint used by nll.com filters."""
    url = "https://www.nll.com/wp-admin/admin-ajax.php"
    payload = {
        "action": "aor_get_all_player_stats",
        "season_id": "225",
        "stage": "REG",
        "team": "",
        "player_type": "",
        "position": "G",
        "current_season": "225",
    }

    response = requests.post(url, data=payload, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    data = response.json()

    html = data.get("html", "")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "all_player_stats"})
    if not table:
        return []

    goalie_rows = []
    for row in table.find("tbody").find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
        if len(cells) < 12:
            continue

        # Columns: Rank, Player, Team, P, GP, MIN, W, L, GA, GAA, SV, SV%
        goalie_rows.append(
            {
                "player_name": cells[1],
                "team": cells[2],
                "position": cells[3],
                "games_played": safe_int(cells[4]),
                "minutes_played": cells[5] or None,
                "wins": safe_int(cells[6]),
                "losses": safe_int(cells[7]),
                "goals_against": safe_int(cells[8]),
                "goals_against_average": safe_float(cells[9]),
                "saves": safe_int(cells[10]),
                "save_percentage": safe_float(cells[11]),
            }
        )

    return goalie_rows


def apply_goalie_stats(session):
    """Update GOALTENDER records with goalie-only stat columns."""
    goalie_rows = fetch_goalie_stats()
    if not goalie_rows:
        print("\n⚠ No goalie rows returned from endpoint.")
        return

    print(f"\nApplying goalie stats for {len(goalie_rows)} goalies...")

    # Build lookup maps for reliable matching.
    goalie_by_name_team = {
        (normalize_key(row["player_name"]), normalize_key(row["team"])): row for row in goalie_rows
    }
    goalie_by_name = {normalize_key(row["player_name"]): row for row in goalie_rows}

    all_goalie_stats = session.exec(
        select(PlayerStats).where(PlayerStats.position == "GOALTENDER")
    ).all()

    updated = 0
    for stat in all_goalie_stats:
        key_exact = (normalize_key(stat.player_name), normalize_key(stat.team))
        goalie = goalie_by_name_team.get(key_exact)
        if goalie is None:
            goalie = goalie_by_name.get(normalize_key(stat.player_name))
        if goalie is None:
            continue

        stat.games_played = goalie["games_played"]
        stat.minutes_played = goalie["minutes_played"]
        stat.wins = goalie["wins"]
        stat.losses = goalie["losses"]
        stat.goals_against = goalie["goals_against"]
        stat.goals_against_average = goalie["goals_against_average"]
        stat.saves = goalie["saves"]
        if goalie["save_percentage"] is not None:
            stat.save_percentage = goalie["save_percentage"]
        elif (goalie["saves"] or 0) == 0 and (goalie["goals_against"] or 0) == 0:
            stat.save_percentage = 0.0
        else:
            stat.save_percentage = None
        session.add(stat)
        updated += 1

    session.commit()
    print(f"✓ Updated goalie columns for {updated} GOALTENDER records")

def load_complete_players():
    """Load players with complete statistics"""
    
    # Load pickled data
    with open('/tmp/nll_complete_stats.pkl', 'rb') as f:
        players_data = pickle.load(f)
    
    session = Session(engine)
    
    print(f"Loading {len(players_data)} players with complete statistics...")
    
    for i, player_data in enumerate(players_data):
        # Create or update player profile
        existing_profile = session.exec(
            select(PlayerProfile).where(PlayerProfile.player_name == player_data['name'])
        ).first()
        
        if not existing_profile:
            profile = PlayerProfile(
                player_name=player_data['name'],
                position=position_map(player_data['position']),
                team=player_data['team'],
            )
            session.add(profile)
            session.flush()
            player_id = profile.player_id
        else:
            player_id = existing_profile.player_id
            existing_profile.position = position_map(player_data['position'])
            existing_profile.team = player_data['team']
            session.add(existing_profile)
            session.flush()
        
        # Create or update player stats with ALL available data
        existing_stats = session.exec(
            select(PlayerStats).where(PlayerStats.player_id == player_id)
        ).first()
        
        if existing_stats:
            # Update existing stats
            stats = existing_stats
            session.delete(stats)
            session.flush()
        
        stats = PlayerStats(
            player_id=player_id,
            player_name=player_data['name'],
            team=player_data['team'],
            position=position_map(player_data['position']),
            season=2026,
            
            # Game Statistics
            games_played=player_data.get('games_played'),
            
            # Scoring Statistics
            goals=player_data.get('goals'),
            assists=player_data.get('assists'),
            points=player_data.get('points'),
            
            # Penalties & Discipline
            penalty_minutes=player_data.get('penalty_minutes'),
            power_play_goals=player_data.get('power_play_goals'),
            power_play_assists=player_data.get('power_play_assists'),
            short_handed_goals=player_data.get('short_handed_goals'),
            
            # Possession & Turnovers
            loose_balls=player_data.get('loose_balls'),
            turnovers=player_data.get('turnovers'),
            caused_turnovers=player_data.get('caused_turnovers'),
            
            # Shot & Defense Statistics
            blocked_shots=player_data.get('blocked_shots'),
            shots_on_goal=player_data.get('shots_on_goal'),
            
            # Faceoff Statistics
            faceoffs_won=player_data.get('faceoffs_won'),
            faceoffs_lost=player_data.get('faceoffs_lost'),
            faceoff_percentage=player_data.get('faceoff_percentage'),
        )
        
        session.add(stats)
        
        if (i + 1) % 50 == 0:
            session.commit()
            print(f"  ✓ Loaded {i + 1} players...")
    
    session.commit()

    # Enrich player_profile rows using individual player profile pages.
    apply_player_profiles(session)
    apply_directory_numbers(session)

    # Enrich goaltenders with goalie-only statistics (W/L/GA/GAA/SV/SV%).
    apply_goalie_stats(session)
    session.close()
    
    # Verify
    print(f"\n✓ Inserted {len(players_data)} complete player records!")
    
    # Show position breakdown
    session = Session(engine)
    positions = {}
    all_stats = session.exec(select(PlayerStats)).all()
    
    for stat in all_stats:
        pos = stat.position
        positions[pos] = positions.get(pos, 0) + 1
    
    print(f"\nPosition breakdown:")
    for pos in sorted(positions.keys()):
        print(f"  {pos:15} {positions[pos]:3} players")
    
    # Show top scorers
    top_scorers = sorted(all_stats, key=lambda x: x.points or 0, reverse=True)[:10]
    print(f"\nTop 10 Scorers (2025-2026):")
    for j, stat in enumerate(top_scorers, 1):
        goals = stat.goals or 0
        assists = stat.assists or 0
        points = stat.points or 0
        print(f"  {j:2}. {stat.player_name:20} - {stat.team:20} - {points:3} pts ({goals}G {assists}A)")
    
    # Show data completeness
    print(f"\nData completeness check:")
    stats_sample = all_stats[0]
    fields_with_data = [
        ('games_played', stats_sample.games_played),
        ('goals', stats_sample.goals),
        ('assists', stats_sample.assists),
        ('points', stats_sample.points),
        ('penalty_minutes', stats_sample.penalty_minutes),
        ('power_play_goals', stats_sample.power_play_goals),
        ('power_play_assists', stats_sample.power_play_assists),
        ('short_handed_goals', stats_sample.short_handed_goals),
        ('loose_balls', stats_sample.loose_balls),
        ('turnovers', stats_sample.turnovers),
        ('caused_turnovers', stats_sample.caused_turnovers),
        ('blocked_shots', stats_sample.blocked_shots),
        ('shots_on_goal', stats_sample.shots_on_goal),
        ('faceoffs_won', stats_sample.faceoffs_won),
        ('faceoffs_lost', stats_sample.faceoffs_lost),
        ('faceoff_percentage', stats_sample.faceoff_percentage),
        ('minutes_played', stats_sample.minutes_played),
        ('wins', stats_sample.wins),
        ('losses', stats_sample.losses),
        ('goals_against', stats_sample.goals_against),
        ('goals_against_average', stats_sample.goals_against_average),
        ('saves', stats_sample.saves),
        ('save_percentage', stats_sample.save_percentage),
    ]
    
    for field, value in fields_with_data:
        non_null = sum(1 for s in all_stats if getattr(s, field) is not None)
        percentage = (non_null / len(all_stats)) * 100
        status = "✓" if percentage > 50 else "⚠"
        print(f"  {status} {field:25} {non_null:3} / {len(all_stats)} ({percentage:5.1f}%)")
    
    session.close()

if __name__ == "__main__":
    load_complete_players()
