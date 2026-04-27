# 🎰 GamblingApp — Gambling Simulation Application

A production-grade Python gambling simulation built with clean layered architecture and MySQL persistence.

---

## Project Structure

```
GamblingApp/
├── main.py                          # Entry point
├── requirements.txt
├── .gitignore
├── README.md
├── sql/
│   └── schema.sql                   # Full MySQL schema
└── app/
    ├── config/
    │   └── db_config.py             # Connection pool & schema bootstrap
    ├── models/                      # Pure data classes / enums
    │   ├── session_enums.py
    │   ├── transaction_type.py
    │   ├── game_result.py
    │   ├── gambler_profile.py
    │   ├── odds_config.py
    │   ├── stake_boundary.py
    │   ├── session_parameters.py
    │   ├── betting_preferences.py
    │   ├── betting_session.py
    │   ├── bet.py
    │   ├── game_record.py
    │   ├── gaming_session.py
    │   ├── pause_record.py
    │   ├── running_totals.py
    │   ├── stake_transaction.py
    │   └── win_loss_statistics.py
    ├── repository/                  # Raw MySQL CRUD
    │   ├── gambler_repository.py
    │   └── stake_repository.py
    ├── services/                    # Business logic
    │   ├── gambler_service.py
    │   ├── betting_service.py
    │   ├── game_session_manager.py
    │   ├── stake_management_service.py
    │   └── win_loss_calculator.py
    ├── strategies/                  # Betting strategies
    │   ├── base_strategy.py
    │   ├── outcome_base.py
    │   ├── martingale_strategy.py
    │   ├── fibonacci_strategy.py
    │   ├── fixed_strategy.py
    │   ├── percentage_strategy.py
    │   ├── random_outcome_strategy.py
    │   └── weighted_probability_strategy.py
    ├── ui/                          # Terminal UI
    │   ├── game_status_display.py
    │   ├── session_summary.py
    │   ├── simple_game_engine.py
    │   └── interactive_menu.py
    ├── utils/
    │   └── validators.py            # Formatting helpers
    ├── validation/                  # Validation + exceptions
    │   ├── exceptions.py
    │   ├── input_validator.py
    │   ├── safe_input_handler.py
    │   ├── validation_config.py
    │   ├── validation_error_type.py
    │   └── validation_result.py
    └── demo/
        └── demo_app.py              # Automated demo (no DB required)
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| MySQL Server | 8.0+ |
| MySQL Workbench | (optional, for visual inspection) |

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the MySQL database

Open MySQL Workbench (or any MySQL client) and run:

```sql
CREATE DATABASE IF NOT EXISTS gambling_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Configure credentials

Set environment variables **or** rely on defaults:

| Variable | Default |
|----------|---------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `3306` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | `root` |
| `DB_NAME` | `gambling_app` |

```bash
# Example – Windows PowerShell
$env:DB_PASSWORD = "your_password"

# Example – Bash
export DB_PASSWORD="your_password"
```

Or pass them directly on the command line:

```bash
python main.py --user root --password secret --database gambling_app
```

---

## Running the Application

```bash
# Interactive menu (requires MySQL)
python main.py

# Automated demo – all 6 strategies, no DB required
python main.py --demo

# Test DB connection only
python main.py --test-db
```

---

## Betting Strategies

| Strategy | Description |
|----------|-------------|
| **Martingale** | Double stake on loss, reset to base on win |
| **Fibonacci** | Follow Fibonacci sequence on losses, retreat 2 steps on win |
| **Fixed** | Always bet the same base stake |
| **Percentage** | Bet a fixed % of current bankroll each round |
| **Random Outcome** | Uniform random stake within min/max boundary |
| **Weighted Probability** | Stake scales with win probability via linear interpolation |

---

## Stop Conditions

A session ends automatically when **any** of the following trigger:

- **Bankrupt** — bankroll drops to $0 or below
- **Stop-Loss** — bankroll falls below the configured stop-loss threshold
- **Take-Profit** — bankroll reaches or exceeds the take-profit target
- **Max Rounds** — the configured maximum number of rounds is reached

---

## Database Schema

The schema is auto-applied on first run. Tables created:

- `gamblers` — player profiles & bankrolls
- `betting_sessions` — named sessions with strategy config
- `bets` — individual bet records
- `stake_transactions` — deposit / withdrawal / win / loss ledger
- `game_records` — raw RNG outcomes per round
- `win_loss_statistics` — aggregated stats per session
- `pause_records` — pause/resume history

---

## Architecture

```
UI Layer          ← interactive_menu, game_status_display, session_summary
    │
Service Layer     ← gambler_service, betting_service, game_session_manager
    │
Repository Layer  ← gambler_repository, stake_repository (raw SQL)
    │
Database          ← MySQL via mysql-connector-python
```

Models and strategies are pure Python with no framework dependencies.
