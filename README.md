# NLL Box Lacrosse Stats Tracker

A modern web application for viewing National Lacrosse League (NLL) player statistics and performance data.

## Features

- 🥍 **Lacrosse-Themed UI** - Sports-inspired design with NLL color scheme (red, black, gold)
- 📊 **Player Statistics** - View comprehensive stats for all players including:
  - Goals, Assists, Points
  - Shooting Percentage
  - Faceoff Statistics
  - Defensive Stats (for defensemen)
  - Goalie Stats (saves, GAA, wins)
- 🔍 **Search & Filter** - Find players by name, team, or position
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast API Backend** - Built with FastAPI and SQLModel

## Project Structure

```
├── main.py                 # FastAPI backend server
├── models.py               # SQLModel definitions (Bio, Stats)
├── boxlacrosse.db          # SQLite database
├── static/
│   ├── index.html          # Frontend HTML
│   ├── script.js           # Frontend JavaScript
│   └── style.css           # Lacrosse-themed styling
└── README.md               # This file
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip

### Dependencies
```bash
pip install fastapi uvicorn sqlmodel sqlalchemy
```

## Running the Application

1. **Navigate to project directory:**
   ```bash
   cd /workspaces/Midterm-Project---NLL-Stats
   ```

2. **Start the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Access the application:**
   - Open your browser and navigate to `http://localhost:8000`
   - The app will load the player statistics interface

## API Endpoints

### Get All Players
- **GET** `/api/players`
- Returns a list of all players with basic stats

Example Response:
```json
[
  {
    "player_name": "John Doe",
    "team": "Team Name",
    "position": "ATTACK",
    "goals": 45,
    "assists": 28,
    "points": 73,
    "games_played": 18,
    "shooting_percentage": 32.5,
    "plus_minus": 12
  }
]
```

### Get Player Details
- **GET** `/api/players/{player_name}`
- Returns detailed information including bio and complete statistics

## Database Schema

### Bio Table
Stores player biographical information:
- `player_name` (PK): Player's full name
- `number`: Jersey number
- `position`: Player position (ATTACK, MIDFIELD, DEFENSE, GOALIE)
- `team`: Team name
- `age`: Player age
- `hometown`: Player's hometown
- `birthdate`: Date of birth
- `weight`: Player weight
- `shoots`: Handedness (Right/Left)

### Stats Table
Stores player performance statistics:
- `player_name` (FK): Reference to Bio table
- `team`: Team affiliation
- `position`: Playing position
- `goals`: Total goals scored
- `assists`: Total assists
- `points`: Total points (goals + assists)
- `plus_minus`: +/- rating
- `shooting_percentage`: Goals/Shots percentage
- And more... (see models.py for complete list)

## UI Features

### Player Card
- Quick stats overview with position and team
- Color-coded position badges
- One-click access to detailed stats

### Search & Filter
- Real-time player search by name, team, or position
- Position-based filtering (Attack, Midfield, Defense, Goalie)
- Reset button to clear all filters

### Player Detail Modal
- Comprehensive player biography
- Complete season statistics
- Special stats for goalies
- Responsive modal design

## Styling

The app uses a professional lacrosse theme featuring:
- **Primary Color**: Dark Navy (#1a1a1a)
- **Secondary Color**: NLL Red (#c8102e)
- **Accent Color**: Gold (#ffc72c)
- **Typography**: Clean, modern sans-serif fonts
- **Animations**: Smooth transitions and hover effects
- **Responsive Grid**: Adapts to all screen sizes

## Technologies

- **Backend**: FastAPI, Python 3
- **Database**: SQLite with SQLModel ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with responsive design

## Development

To modify the app:

1. Edit `main.py` for backend logic or API endpoints
2. Edit `models.py` to change database schema
3. Edit `static/index.html` for HTML structure
4. Edit `static/style.css` for styling
5. Edit `static/script.js` for frontend functionality

## Future Enhancements

- Add player search by various stat thresholds
- Implement sorting by different statistics
- Add comparative stats between players
- Player statistics charts and graphs
- Team standings and rankings
- Historical statistics and trends

---

**NLL Box Lacrosse Stats** - A project showcasing modern web development with FastAPI and responsive design