# 🎰 Bingo Game System

A full-featured web-based Bingo game platform built with Flask. Host bingo games with multiple game modes, manage digital and paper cards, and display live game monitoring with animated winning patterns.

## Features

### 🎮 Game Modes
- **Classic** - Traditional bingo (5 in a row - horizontal, vertical, or diagonal)
- **Speed** - Fast-paced (any 5 in a row pattern)
- **4 Corners** - Quick win (just the 4 corner squares)
- **Coverall** - Ultimate challenge (mark all 25 squares)

### 🖥️ Core Functionality
- **Number Calling** - Admin control panel to call numbers (1-75) with undo and reset capabilities
- **Live Monitor** - Real-time display of last called numbers with animated winning patterns
- **Dynamic Game Modes** - Switch between game modes on-the-fly
- **Digital Cards** - Generate and mark bingo cards digitally
- **Paper Card Support** - Register and manage physical bingo cards
- **Admin Dashboard** - Manage all player cards and track bingo winners
- **Responsive Design** - Works on desktop, tablet, and mobile devices

### ✨ Visual Features
- **Animated Balls** - Colorful balls bounce and spin when numbers are called
- **Animated Patterns** - Winning pattern board shows 10 different 5-in-a-row patterns that cycle and pulse
- **Real-time Sync** - All displays update automatically without page refresh
- **Beautiful UI** - Purple gradient background with glass-morphism effects
- **Mobile Optimized** - Adapts layout for smaller screens

## Project Structure

```
Bingo/
├── main.py                          # Flask application & backend logic
├── README.md                        # This file
├── game_modes_guide.html           # Game modes reference guide
├── templates/
│   ├── home.html                   # Login page
│   ├── control.html                # Admin number calling interface
│   ├── monitor.html                # Live game monitor display
│   ├── register_card.html          # Card registration page
│   ├── digital_card.html           # Digital card display & marking
│   ├── admin_cards.html            # Admin card management dashboard
│   ├── admin_add_paper_card.html   # Add physical cards interface
│   ├── admin_paper_cards.html      # Paper cards management
│   ├── card_not_found.html         # Error page for invalid cards
│   └── index.html                  # Alternative home page
├── instance/                       # Flask instance folder (auto-created)
└── bingo.db                        # SQLite database (auto-created)
```

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd Bingo
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open in browser**
   - Navigate to `http://localhost:5000`
   - Default admin password: `admin`

## Configuration

Edit the following variables in `main.py` to customize your game:

```python
NUM_MONITOR_BALLS = 3           # How many balls to show in monitor (1-5 recommended)
TOTAL_BALLS = 75                # Total numbers in game (75 for standard bingo)
GAME_MODES = ["Classic", "4 corners", "Speed", "Coverall"]  # Available modes
ADMIN_PASSWORD = "admin"        # Change to secure password
```

## Usage Guide

### For Game Host/Admin

1. **Start the Game**
   - Open `http://localhost:5000`
   - Log in with admin password
   - Go to Control page
   - Click numbers to call them or use the number grid
   - Use Undo to retract a number, Reset to clear all

2. **Switch Game Mode**
   - Use the game mode selector in the control panel
   - Monitor display updates instantly with new winning pattern

3. **Manage Cards**
   - Visit Admin Cards to view all registered players
   - See who has achieved bingo
   - Track by round number

### For Players

1. **Register Your Card**
   - Go to Register Card page
   - Enter your card ID and name
   - Digital card generates automatically (or upload paper card numbers)

2. **Play Digital Card**
   - Enter your card ID on the card lookup page
   - Click numbers as they're called to mark them
   - Get instant bingo notification when you win

3. **Monitor Display**
   - Opens on separate screen/projector
   - Shows last 3 called numbers with BINGO letters
   - Displays current game mode
   - Shows winning pattern pattern for current mode
   - Updates in real-time as numbers are called

## Game Modes Explained

### Classic
- **Win Condition**: Complete any 5 in a row (horizontal, vertical, or diagonal)
- **Speed**: Moderate
- **Display**: Cycles through different 5-in-a-row patterns every update
- **Animation**: Green pulses on required squares

### Speed
- **Win Condition**: Same as Classic (any 5 in a row)
- **Speed**: Fast - wins happen quickly
- **Display**: Shows different patterns rapidly
- **Best for**: Quick-paced games

### 4 Corners
- **Win Condition**: Mark only the 4 corner squares
- **Speed**: Very fast - quickest possible win
- **Squares Needed**: 4 (top-left, top-right, bottom-left, bottom-right)
- **Best for**: Warm-up rounds

### Coverall
- **Win Condition**: Mark all 25 squares on your card
- **Speed**: Slowest - longest game
- **Squares Needed**: 25
- **Difficulty**: Hard
- **Best for**: Grand prize rounds

## API Endpoints

### Public Endpoints
- `GET /` - Home/login page
- `GET /register-card` - Card registration form
- `GET /monitor` - Live monitor display
- `GET /card/<card_id>` - Player's digital card

### API Routes
- `POST /api/call/<number>` - Call a number
- `POST /api/undo` - Undo last number
- `POST /api/reset` - Reset all called numbers
- `GET /api/state` - Get current game state
- `POST /api/game-mode/<mode>` - Switch game mode
- `POST /api/register-card` - Register new card
- `POST /api/mark-number` - Mark number on card

### Admin Endpoints (require login)
- `GET /control` - Number calling interface
- `GET /admin-cards` - Card management dashboard
- `POST /admin-check-bingo/<card_id>` - Check/mark bingo manually

## Database Schema

### BingoCard Table
```
- id (Integer, Primary Key)
- card_id (String, Unique) - Player's card identifier
- player_name (String) - Player's name
- numbers (String) - 25 comma-separated numbers
- round_number (Integer) - Game round
- has_bingo (Boolean) - Bingo status
- marked_numbers (String) - Comma-separated marked numbers
- created_at (DateTime) - Card creation timestamp
```

## Browser Compatibility

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅

## Tips for Best Experience

1. **Use Projector/TV for Monitor** - Display monitor on a large screen visible to all players
2. **Separate Screens** - Run control panel and monitor on different windows/devices
3. **Secure Password** - Change admin password from default
4. **Backup Database** - Periodically back up `bingo.db` for game history
5. **Test Before Game** - Verify all cards are registered before starting

## Troubleshooting

### Numbers not updating on monitor?
- Check browser console for errors (F12)
- Ensure both windows are on same network if using different devices
- Refresh monitor page

### Cards not registering?
- Check card ID is unique
- Ensure player name is not empty
- SQLite database might be locked - restart application

### Game mode not changing?
- Verify mode name matches exactly
- Check that mode is in GAME_MODES list in main.py

## Future Enhancements

- User authentication for players
- Game statistics and leaderboards
- Multiple language support
- Dark mode toggle
- Email notifications for winners
- Progressive web app support

## License

Open source - free to use and modify

## Support

For issues or questions, check the code comments in main.py and template files for detailed explanations of functionality.

---

**Enjoy your Bingo games!** 🎉
