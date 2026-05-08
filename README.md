#  Calculative Gambling Simulation App
### Python + MySQL | Modular Architecture | Production-Ready

A fully modular, database-backed gambling simulation system built with **Python** and **MySQL**. Simulates a calculative gambler who manages stake through strategic betting, with defined upper and lower limits that trigger exit conditions.

---

##  Project Overview

This project models a complete gambling lifecycle — from gambler profile creation to session management, betting strategies, win/loss calculation, and real-time stake tracking — all backed by a normalized relational database and a rich CLI interface.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.x** | Core application language |
| **MySQL 8+** | Relational database |
| **mysql-connector-python** | DB connectivity (no ORM) |
| **python-dotenv** | Environment configuration |
| **rich** | CLI display and logging |

---

##  Project Structure

```
gambling-app/
├── main.py                          # Startup orchestration and main loop
├── .env                             # Environment variables (not committed)
├── config/
│   ├── settings.py                  # Load and validate environment values
│   ├── database.py                  # MySQL connection and pooled access
│   └── schema_manager.py            # Idempotent table/index/view creation
├── models/
│   └── *.py                         # Dataclasses for domain objects
├── services/
│   ├── gambler_profile_service.py   # UC-01
│   ├── stake_management_service.py  # UC-02
│   ├── betting_service.py           # UC-03
│   ├── game_session_manager.py      # UC-04
│   └── win_loss_calculator.py       # UC-05
├── strategies/
│   ├── fixed_amount.py
│   ├── percentage.py
│   ├── martingale.py
│   ├── fibonacci.py
│   └── dalembert.py
├── tracking_and_reports/
│   ├── gambler_statistics.py
│   ├── stake_history_report.py
│   └── win_loss_statistics.py
├── ui/
│   ├── game_status_display.py
│   ├── interactive_menu.py
│   └── session_summary.py
└── utils/
    ├── input_validator.py
    ├── exceptions.py
    └── enums.py
```

---

## Database Design (Normalized)

### Relationship Overview
```
GAMBLER
   │
   ├── BETTING_PREFERENCES
   │
   ├── SESSION ─── STRATEGY
   │       │
   │       ├── BET ─── BET_HISTORY
   │       │
   │       └── STAKE_TRANSACTION
   │
   └── STAKE_TRANSACTION
```

### Tables

**1. GAMBLER**
```
gambler_id (PK) | name | initial_balance | current_balance
total_winnings | total_bets | min_balance
win_threshold | loss_threshold | created_at
```

**2. BETTING_PREFERENCES**
```
preference_id (PK) | gambler_id (FK) | min_bet | max_bet
game_type | auto_play_enabled | session_limit | created_at
```

**3. STRATEGY**
```
strategy_id (PK) | name | description
```
Examples: Martingale, Fibonacci, Fixed, Percentage

**4. SESSION**
```
session_id (PK) | gambler_id (FK) | strategy_id (FK)
start_time | end_time | status | initial_balance | ending_balance
upper_limit | lower_limit | timeout | total_games | total_wins | total_losses
```

**5. BET**
```
bet_id (PK) | session_id (FK) | bet_amount | bet_number
probability | strategy_applied | stake_before | stake_after | placed_at
```

**6. BET_HISTORY**
```
history_id (PK) | bet_id (FK) | result (WIN/LOSS)
win_amount | loss_amount | net_change | odds | created_at
```

**7. STAKE_TRANSACTION**
```
transaction_id (PK) | gambler_id (FK) | session_id (FK) | bet_id (FK, nullable)
type (BET_PLACED/WIN/LOSS/DEPOSIT/RESET) | amount | balance_after | created_at
```

---

##  Use Cases (7 Modules)

### UC-01 — Gambler Profile Management
- Create gambler with initial stake, win/loss thresholds
- Update personal info and betting preferences
- Retrieve financial status and statistics
- Validate eligibility based on minimum stake
- Reset profile for a new session

### UC-02 — Stake Management Operations
- Initialize starting stake with validation
- Track real-time balance changes
- Calculate stake after each bet outcome
- Monitor fluctuations (peak, lowest, volatility)
- Validate stake boundaries (upper/lower limits)
- Generate stake history reports

### UC-03 — Betting Mechanism
- Place single/multiple bets with validation
- Determine outcomes using probability
- Apply stake changes based on win/loss
- Support multiple betting strategies

**Strategies supported:**

| Strategy | Description |
|---|---|
| Fixed Amount | Always bet the same amount |
| Percentage | Bet a % of current stake |
| Martingale | Double after loss, reset after win |
| Reverse Martingale | Double after win, reset after loss |
| Fibonacci | Progress through Fibonacci sequence on losses |
| D'Alembert | Gradually increase/decrease by fixed increment |

### UC-04 — Game Session Management
- Start session with configurable parameters
- Continue while stake stays within boundaries
- Pause and resume with duration tracking
- Auto-end on upper limit (win) or lower limit (loss)
- Track total duration, active time, pause time

### UC-05 — Win/Loss Calculation
- Determine outcomes (random / probability-weighted)
- Calculate payouts based on odds type (Fixed / American / Decimal / Probability-based)
- Maintain running totals and win/loss ratios
- Track consecutive win/loss streaks
- Compute ROI, profit factor, win rate

### UC-06 — Input Validation and Error Handling
- Validate initial stake (positive, within range)
- Ensure bet does not exceed current stake
- Verify upper limit > lower limit
- Handle invalid numeric inputs (NaN, Infinity, null)
- Prevent negative stake values
- Validate probability values within [0.0, 1.0]

### UC-07 — User Interaction
- Display current stake and session status
- Prompt for bet input with validation
- Show game outcome and updated stake
- Present full session summary at conclusion
- Interactive menu for all operations

---

##  Setup & Installation

### Prerequisites
- Python 3.x
- MySQL 8+

### Step 1: Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/gambling-app.git
cd gambling-app
```

### Step 2: Install dependencies
```bash
pip install mysql-connector-python python-dotenv rich
```

### Step 3: Create your `.env` file
```env
APP_NAME=GamblingApp
APP_ENV=dev
APP_DEBUG=true

DB_HOST=localhost
DB_PORT=3306
DB_NAME=gambling_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_CHARSET=utf8mb4
DB_AUTOCOMMIT=false

SESSION_DEFAULT_WIN_PROBABILITY=0.5
SESSION_DEFAULT_MAX_GAMES=100
SESSION_DEFAULT_MAX_MINUTES=60

VALIDATION_STRICT_MODE=true
MIN_INITIAL_STAKE=100.00
MAX_INITIAL_STAKE=100000.00
```

### Step 4: Run the application
```bash
python main.py
```

Tables are auto-created on startup using `CREATE TABLE IF NOT EXISTS`.

---

## Startup Behavior

On every startup the app will:
1. Load `.env` with `python-dotenv`
2. Validate all required settings
3. Connect to MySQL
4. Create database if it does not exist
5. Create all tables in deterministic order
6. Seed static lookup data (strategies, odds configs)
7. Display startup summary using `rich`

**Table creation order:**
```
GAMBLERS → BETTING_PREFERENCES → SESSIONS → SESSION_PARAMETERS
→ BETTING_STRATEGIES → ODDS_CONFIGURATIONS → BETS → GAME_RECORDS
→ STAKE_TRANSACTIONS → PAUSE_RECORDS → RUNNING_TOTALS_SNAPSHOTS
→ VALIDATION_EVENTS
```

---

##  Key Design Decisions

- **No ORM** — Direct SQL using `mysql-connector-python` for full control
- **Immutable audit trail** — `STAKE_TRANSACTIONS` records every balance movement
- **Decimal precision** — All monetary values use `DECIMAL`, never floating point
- **Transaction safety** — Every bet flow wrapped in a DB transaction
- **Session locking** — Active session row locked before mutation to avoid race conditions
- **Idempotent startup** — `IF NOT EXISTS` used on all table and index creation

---

##  Reporting Views (SQL)

| View | Purpose |
|---|---|
| `vw_gambler_statistics` | Profile + aggregated bets/wins/losses/net |
| `vw_session_summary` | Duration, games played, win rate, ROI |
| `vw_stake_history` | Ordered transaction timeline with delta values |

---

##  Validation Coverage

| Validation Type | Checks |
|---|---|
| Stake | Positive, non-negative, within range |
| Bet | Min/max limits, does not exceed current stake |
| Limits | Upper > lower, initial stake in range |
| Probability | Bounded [0.0, 1.0] |
| Numeric | Null, NaN, Infinity, string parse failures |
| Session | Active status and boundary check each game |

---

##  Build Roadmap

- [x] ER model and schema design
- [ ] `settings.py` and `.env` bootstrap
- [ ] `schema_manager.py` with startup table creation
- [ ] UC-01: Gambler Profile Management
- [ ] UC-02: Stake Management Operations
- [ ] UC-03: Betting Mechanism + Strategies
- [ ] UC-04: Game Session Management
- [ ] UC-05: Win/Loss Statistics and Reporting Views
- [ ] UC-06: Input Validation and Error Handling
- [ ] UC-07: Rich CLI Interface and Interactive Menu

---

##  Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

---

##  License

This project is for educational and simulation purposes only. No real gambling is involved.
