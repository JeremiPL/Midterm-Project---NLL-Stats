# NLL Box Lacrosse Stats - Setup & Usage Guide

## ✅ System Setup Complete

Your NLL Stats application is now fully functional with:

- ✓ Updated database models for Player Profiles and Statistics
- ✓ 10 realistic 2024 NLL season players with comprehensive stats
- ✓ Fully functional FastAPI backend with REST endpoints
- ✓ Responsive lacrosse-themed frontend with search & filter
- ✓ New position labels: Forward, Transition, Defence, Goaltender

---

## 📁 Database Schema

### player_profile Table
Stores player biographical information:
- `player_id` (Primary Key)
- `player_name`, `number`, `position`, `team`
- `age`, `height`, `weight`, `hometown`, `birthdate`
- `shoots`, `college`, `drafted`

### player_stats Table
Stores comprehensive player statistics:
- `stat_id` (Primary Key)
- `player_id` (Foreign Key to player_profile)
- **Scoring:** goals, assists, points, plus_minus, shooting_percentage
- **Game Info:** games_played, games_started, season
- **Advanced:** loose_balls, turnovers, ground_balls, penalty_minutes
- **Position-specific:**
  - Forwards/Transition: faceoffs_won, faceoffs_lost, faceoff_percentage
  - Defensemen: caused_turnovers, defensive_ground_balls
  - Goaltenders: saves, goals_against, GAA, wins, losses, save_percentage

---

## 🚀 Running the Application

### Step 1: Start the Server
```bash
cd /workspaces/Midterm-Project---NLL-Stats
uvicorn main:app --reload --port 8000
```

Or use FastAPI CLI:
```bash
fastapi dev main.py
```

### Step 2: Access the App
Open your browser and go to:
```
http://localhost:8000
```

The app will automatically load all 10 NLL players from the database.

---

## 📊 API Endpoints

### Get All Players
```
GET /api/players
```
Returns a list of all players with basic stats.

**Response Example:**
```json
[
  {
    "player_id": 1,
    "player_name": "Connor Fields",
    "team": "Toronto Rock",
    "position": "FORWARD",
    "number": 2,
    "goals": 47,
    "assists": 35,
    "points": 82,
    "games_played": 18,
    "shooting_percentage": 33.1,
    "plus_minus": 8
  }
]
```

### Get Player Details
```
GET /api/players/{player_id}
```
Returns comprehensive profile and statistics for a specific player.

**Response Example:**
```json
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
    "games_played": 18,
    "goals": 47,
    "assists": 35,
    "points": 82,
    "plus_minus": 8,
    "shooting_percentage": 33.1,
    ...
  }
}
```

---

## 🎮 Frontend Features

### Search
- Search players by name, team, or position
- Real-time filtering as you type
- Clear search results with "Reset" button

### Filters
- **All Players**: Show all roster members
- **Forward**: Show forward position players
- **Transition**: Show transition position players  
- **Defence**: Show defence position players
- **Goaltender**: Show goaltender position players

### Player Cards
- Quick view of player name, number, position, and key stats
- Goal/Assist/Points/Games Played summary
- Click "View Details" for comprehensive statistics
- Team-based card and modal colors are applied automatically
- Team logos display when logo files are present in `static/team-logos/`

### Team Logos (Optional)
You can add official team logos for cards and modals.

1. Place logo files in `static/team-logos/`
2. Use the exact filenames listed in `static/team-logos/README.md`
3. Missing files will automatically fall back to `static/team-logos/default-logo.svg`

### Detailed View Modal
- Full player profile information
- Complete statistical breakdown
- Position-specific stats (faceoff %, save %, etc.)

---

## 📈 Current Roster (2024 Season)

| Player | Position | Team | GP | G | A | Pts |
|--------|----------|------|----|----|----|----|
| Dan Dawson | Forward | Buffalo Bandits | 18 | 56 | 42 | 98 |
| Dhane Smith | Forward | Buffalo Bandits | 18 | 52 | 38 | 90 |
| Connor Fields | Forward | Toronto Rock | 18 | 47 | 35 | 82 |
| Charlotte Muller | Forward | Toronto Rock | 18 | 44 | 38 | 82 |
| Corey Small | Transition | Toronto Rock | 18 | 35 | 46 | 81 |
| Kyle Killen | Transition | Toronto Rock | 18 | 28 | 52 | 80 |
| Mark Steenhuis | Transition | Buffalo Bandits | 18 | 32 | 48 | 80 |
| Challen Rogers | Defence | Toronto Rock | 18 | 8 | 16 | 24 |
| Ryan Dilks | Defence | Toronto Rock | 18 | 6 | 14 | 20 |
| Cody Jamieson | Goaltender | Buffalo Bandits | 14 | 0 | 0 | 0 |

---

## 🔧 Adding More Players

### Option 1: Use the Population Script
Edit `populate_db.py` to add more player data in the `PLAYERS_DATA` list, then run:
```bash
python3 populate_db.py
```

### Option 2: Manual Database Query
```python
from sqlmodel import Session
from models import engine, PlayerProfile, PlayerStats

with Session(engine) as session:
    profile = PlayerProfile(
        player_id=11,
        player_name="New Player",
        position="FORWARD",
        team="Some Team",
        # ... other fields
    )
    session.add(profile)
    
    stats = PlayerStats(
        player_id=11,
        player_name="New Player",
        team="Some Team",
        position="FORWARD",
        season=2024,
        # ... other stats fields
    )
    session.add(stats)
    session.commit()
```

---

## 🛠 Tech Stack

- **Backend:** FastAPI, Python 3.x, SQLModel, SQLite
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** SQLite (boxlacrosse.db)
- **Styling:** Responsive NLL-themed CSS with red (#c8102e), black, and gold (#ffc72c)

---

## 📝 File Structure

```
.
├── main.py                      # FastAPI server
├── models.py                    # SQLModel definitions
├── populate_db.py              # Data population script
├── boxlacrosse.db              # SQLite database
├── README.md                   # Documentation
├── SETUP.md                    # This file
└── static/
    ├── index.html
    ├── script.js
    └── style.css
```

---

## 🐛 Troubleshooting

### No players showing on the app?
1. Ensure the database is populated: `python3 populate_db.py`
2. Verify the API is running: `curl http://localhost:8000/api/players`
3. Check browser console for JavaScript errors (F12)

### API returns 404?
- Make sure the server is running (`uvicorn main:app --reload`)
- Check that FastAPI is listening on port 8000

### Search not working?
- Clear browser cache (Ctrl+Shift+Delete)
- Reload the page (F5)
- Check that player data exists in database

### Filter buttons not working?
- Ensure JavaScript is enabled
- Check browser console for errors
- Verify the positions in database match the filter names

---

## 🚀 Future Enhancements

Potential features to add:
- Player comparison tool
- Team statistics and rankings
- Historical season data
- Advanced filtering (by stats range)
- Player statistics charts and graphs
- Export data to CSV
- Admin panel for managing players
- User authentication for coaches/managers

---

## ✨ Summary of Changes

1. **Updated Database Model** - Separated player profile and statistics into two tables
2. **New Position Names** - Changed from Attack/Midfield/Defense/Goalie to Forward/Transition/Defence/Goaltender
3. **Realistic Data** - Added 10 authentic-looking 2024 NLL season data
4. **Backend Optimization** - Updated FastAPI to work with new models and use player_id instead of names
5. **Frontend Updates** - Updated buttons, position labels, and API calls throughout
6. **Population Script** - Created `populate_db.py` for easy database management

---

**Application ready to use! 🎉**
