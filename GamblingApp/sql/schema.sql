-- ============================================================
-- GamblingApp Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS gambling_app
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gambling_app;

-- ============================================================
-- Table: gamblers
-- ============================================================
CREATE TABLE IF NOT EXISTS gamblers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(100)    NOT NULL UNIQUE,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    initial_bankroll DECIMAL(15,2)  NOT NULL CHECK (initial_bankroll > 0),
    current_bankroll DECIMAL(15,2)  NOT NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active       BOOLEAN         DEFAULT TRUE
);

-- ============================================================
-- Table: betting_sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS betting_sessions (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    gambler_id              INT             NOT NULL,
    session_name            VARCHAR(255),
    strategy_type           VARCHAR(50)     NOT NULL,
    initial_stake           DECIMAL(15,2)   NOT NULL,
    min_stake               DECIMAL(15,2)   NOT NULL,
    max_stake               DECIMAL(15,2)   NOT NULL,
    stop_loss_threshold     DECIMAL(15,2),
    take_profit_threshold   DECIMAL(15,2),
    max_rounds              INT,
    win_probability         DECIMAL(8,6)    DEFAULT 0.500000,
    payout_multiplier       DECIMAL(8,4)    DEFAULT 2.0000,
    strategy_param          DECIMAL(8,4),
    status                  VARCHAR(20)     DEFAULT 'ACTIVE',
    started_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    ended_at                TIMESTAMP       NULL,
    FOREIGN KEY (gambler_id) REFERENCES gamblers(id) ON DELETE CASCADE,
    INDEX idx_gambler_id (gambler_id),
    INDEX idx_status (status)
);

-- ============================================================
-- Table: bets
-- ============================================================
CREATE TABLE IF NOT EXISTS bets (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL,
    gambler_id          INT             NOT NULL,
    round_number        INT             NOT NULL,
    stake_amount        DECIMAL(15,2)   NOT NULL,
    game_result         VARCHAR(10)     NOT NULL,
    payout              DECIMAL(15,2)   NOT NULL,
    profit_loss         DECIMAL(15,2)   NOT NULL,
    bankroll_after      DECIMAL(15,2)   NOT NULL,
    strategy_next_stake DECIMAL(15,2),
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id)  REFERENCES betting_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (gambler_id)  REFERENCES gamblers(id)         ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_gambler_id (gambler_id),
    INDEX idx_round (session_id, round_number)
);

-- ============================================================
-- Table: stake_transactions
-- ============================================================
CREATE TABLE IF NOT EXISTS stake_transactions (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    gambler_id          INT             NOT NULL,
    session_id          INT,
    transaction_type    VARCHAR(20)     NOT NULL,
    amount              DECIMAL(15,2)   NOT NULL,
    balance_before      DECIMAL(15,2)   NOT NULL,
    balance_after       DECIMAL(15,2)   NOT NULL,
    description         VARCHAR(500),
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gambler_id) REFERENCES gamblers(id)          ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES betting_sessions(id)  ON DELETE SET NULL,
    INDEX idx_gambler_id (gambler_id),
    INDEX idx_session_id (session_id)
);

-- ============================================================
-- Table: game_records
-- ============================================================
CREATE TABLE IF NOT EXISTS game_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      INT             NOT NULL,
    bet_id          INT,
    round_number    INT             NOT NULL,
    game_type       VARCHAR(50)     DEFAULT 'COIN_FLIP',
    outcome         VARCHAR(10)     NOT NULL,
    win_probability DECIMAL(8,6),
    random_value    DECIMAL(12,10),
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES betting_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (bet_id)     REFERENCES bets(id)             ON DELETE SET NULL,
    INDEX idx_session_id (session_id)
);

-- ============================================================
-- Table: win_loss_statistics
-- ============================================================
CREATE TABLE IF NOT EXISTS win_loss_statistics (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL UNIQUE,
    gambler_id          INT             NOT NULL,
    total_bets          INT             DEFAULT 0,
    total_wins          INT             DEFAULT 0,
    total_losses        INT             DEFAULT 0,
    total_staked        DECIMAL(15,2)   DEFAULT 0.00,
    total_payout        DECIMAL(15,2)   DEFAULT 0.00,
    net_profit_loss     DECIMAL(15,2)   DEFAULT 0.00,
    win_rate            DECIMAL(8,6)    DEFAULT 0.000000,
    max_win_streak      INT             DEFAULT 0,
    max_loss_streak     INT             DEFAULT 0,
    current_win_streak  INT             DEFAULT 0,
    current_loss_streak INT             DEFAULT 0,
    peak_bankroll       DECIMAL(15,2)   DEFAULT 0.00,
    lowest_bankroll     DECIMAL(15,2)   DEFAULT 0.00,
    updated_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES betting_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (gambler_id) REFERENCES gamblers(id)         ON DELETE CASCADE
);

-- ============================================================
-- Table: pause_records
-- ============================================================
CREATE TABLE IF NOT EXISTS pause_records (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    session_id  INT         NOT NULL,
    paused_at   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    resumed_at  TIMESTAMP   NULL,
    reason      VARCHAR(255),
    FOREIGN KEY (session_id) REFERENCES betting_sessions(id) ON DELETE CASCADE
);
