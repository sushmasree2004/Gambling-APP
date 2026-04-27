"""
Interactive terminal menu for the GamblingApp.
Ties all services together with a human-friendly UI.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.models.betting_preferences import BettingPreferences
from app.models.odds_config import OddsConfig
from app.models.session_enums import StrategyType
from app.models.session_parameters import SessionParameters
from app.models.stake_boundary import StakeBoundary
from app.services.betting_service import BettingService
from app.services.gambler_service import GamblerService
from app.services.game_session_manager import GameSessionManager
from app.strategies.fibonacci_strategy import FibonacciStrategy
from app.strategies.fixed_strategy import FixedStrategy
from app.strategies.martingale_strategy import MartingaleStrategy
from app.strategies.percentage_strategy import PercentageStrategy
from app.strategies.random_outcome_strategy import RandomOutcomeStrategy
from app.strategies.weighted_probability_strategy import WeightedProbabilityStrategy
from app.ui.session_summary import SessionSummary
from app.ui.simple_game_engine import SimpleGameEngine
from app.utils.validators import banner, format_currency, mini_banner
from app.validation.exceptions import (
    DuplicateRecordError,
    GamblerNotFoundError,
    GamblingAppError,
    SessionAlreadyActiveError,
)
from app.validation.safe_input_handler import SafeInputHandler


class InteractiveMenu:
    def __init__(self) -> None:
        self._gambler_svc = GamblerService()
        self._session_mgr = GameSessionManager()
        self._bet_svc     = BettingService()
        self._engine      = SimpleGameEngine(delay_seconds=0.05)
        self._io          = SafeInputHandler()

    # ════════════════════════════════════════════════════════════════════════
    # MAIN MENU
    # ════════════════════════════════════════════════════════════════════════

    def run(self) -> None:
        print(banner("🎲  GAMBLING SIMULATION APP  🎲"))
        while True:
            print(mini_banner("Main Menu"))
            print("  1. Manage Gamblers")
            print("  2. Start a New Session")
            print("  3. View Session History")
            print("  4. Quit")
            choice = self._io.get_menu_choice("  Choice: ", range(1, 5))
            if choice is None:
                continue
            if choice == 1:
                self._gambler_menu()
            elif choice == 2:
                self._new_session_flow()
            elif choice == 3:
                self._session_history_flow()
            elif choice == 4:
                print("\n  Goodbye! 🎲\n")
                break

    # ════════════════════════════════════════════════════════════════════════
    # GAMBLER MANAGEMENT
    # ════════════════════════════════════════════════════════════════════════

    def _gambler_menu(self) -> None:
        while True:
            print(mini_banner("Gambler Menu"))
            print("  1. Create New Gambler")
            print("  2. List All Gamblers")
            print("  3. View Gambler Details")
            print("  4. Deposit Funds")
            print("  5. Withdraw Funds")
            print("  6. Back")
            choice = self._io.get_menu_choice("  Choice: ", range(1, 7))
            if choice is None or choice == 6:
                return
            {1: self._create_gambler,
             2: self._list_gamblers,
             3: self._view_gambler,
             4: self._deposit,
             5: self._withdraw}[choice]()

    def _create_gambler(self) -> None:
        print(mini_banner("Create Gambler"))
        username  = self._io.get_username("  Username : ")
        email     = self._io.get_email("  Email    : ")
        bankroll  = self._io.get_decimal("  Starting bankroll ($): ", Decimal("1"), Decimal("10000000"))
        if None in (username, email, bankroll):
            print("  Cancelled.")
            return
        try:
            g = self._gambler_svc.create_gambler(username, email, bankroll)
            print(f"\n  ✅  Gambler created!  ID={g.id}  Bankroll={format_currency(g.current_bankroll)}")
        except DuplicateRecordError as e:
            print(f"  ✗ {e}")
        except GamblingAppError as e:
            print(f"  ✗ {e}")

    def _list_gamblers(self) -> None:
        gamblers = self._gambler_svc.list_all()
        if not gamblers:
            print("  No gamblers registered yet.")
            return
        print(mini_banner("Registered Gamblers"))
        print(f"  {'ID':<5} {'Username':<20} {'Bankroll':>14} {'P/L':>12}")
        print(f"  {'─'*56}")
        for g in gamblers:
            sign = "+" if g.profit_loss >= 0 else ""
            print(f"  {g.id:<5} {g.username:<20} "
                  f"{format_currency(g.current_bankroll):>14} "
                  f"{sign}{format_currency(g.profit_loss):>12}")

    def _view_gambler(self) -> None:
        gid = self._io.get_int("  Gambler ID: ", 1)
        if gid is None:
            return
        try:
            g = self._gambler_svc.get_gambler(gid)
            print(mini_banner(f"Gambler: {g.username}"))
            for k, v in g.to_dict().items():
                print(f"  {k:<25}: {v}")
        except GamblerNotFoundError as e:
            print(f"  ✗ {e}")

    def _deposit(self) -> None:
        gid = self._io.get_int("  Gambler ID: ", 1)
        amt = self._io.get_decimal("  Amount ($): ", Decimal("0.01"))
        if None in (gid, amt):
            return
        try:
            g = self._gambler_svc.deposit(gid, amt)
            print(f"  ✅  New balance: {format_currency(g.current_bankroll)}")
        except GamblingAppError as e:
            print(f"  ✗ {e}")

    def _withdraw(self) -> None:
        gid = self._io.get_int("  Gambler ID: ", 1)
        amt = self._io.get_decimal("  Amount ($): ", Decimal("0.01"))
        if None in (gid, amt):
            return
        try:
            g = self._gambler_svc.withdraw(gid, amt)
            print(f"  ✅  New balance: {format_currency(g.current_bankroll)}")
        except GamblingAppError as e:
            print(f"  ✗ {e}")

    # ════════════════════════════════════════════════════════════════════════
    # NEW SESSION FLOW
    # ════════════════════════════════════════════════════════════════════════

    def _new_session_flow(self) -> None:
        print(mini_banner("New Betting Session"))

        # Pick gambler
        gid = self._io.get_int("  Gambler ID: ", 1)
        if gid is None:
            return
        try:
            gambler = self._gambler_svc.get_gambler(gid)
        except GamblerNotFoundError as e:
            print(f"  ✗ {e}"); return
        print(f"  Gambler: {gambler.username}  |  Bankroll: {format_currency(gambler.current_bankroll)}")

        # Session name
        session_name = self._io.get_string("  Session name (or press Enter for default): ",
                                           min_len=0, max_len=255) or ""

        # Strategy
        strategy_type = self._pick_strategy()
        if strategy_type is None:
            return

        # Stake configuration
        print(mini_banner("Stake Configuration"))
        initial_stake = self._io.get_decimal("  Initial / base stake ($): ", Decimal("0.01"),
                                              gambler.current_bankroll)
        min_stake     = self._io.get_decimal("  Min stake ($): ",            Decimal("0.01"),
                                              initial_stake)
        max_stake     = self._io.get_decimal("  Max stake ($): ",            initial_stake,
                                              gambler.current_bankroll)
        if None in (initial_stake, min_stake, max_stake):
            return

        # Odds
        print(mini_banner("Game Odds"))
        win_prob  = self._io.get_float_range("  Win probability (0.01–0.99): ", 0.01, 0.99)
        payout    = self._io.get_decimal("  Payout multiplier (e.g. 2.0 for 1:1): ",
                                          Decimal("1.01"), Decimal("1000"))
        if None in (win_prob, payout):
            return

        # Stop conditions
        print(mini_banner("Stop Conditions"))
        stop_loss  = self._io.get_decimal(
            f"  Stop-loss threshold ($, 0 to skip): ", Decimal("0"), gambler.current_bankroll)
        take_profit = self._io.get_decimal(
            f"  Take-profit threshold ($, 0 to skip): ", Decimal("0"), Decimal("100000000"))
        max_rounds  = self._io.get_int("  Max rounds (0 for unlimited): ", 0, 100000)
        if None in (stop_loss, take_profit, max_rounds):
            return

        # Strategy-specific param
        strategy_param: Optional[Decimal] = None
        if strategy_type == StrategyType.PERCENTAGE:
            strategy_param = self._io.get_decimal(
                "  Bet percentage of bankroll (e.g. 0.05 = 5%): ", Decimal("0.001"), Decimal("1"))

        # Build preferences
        try:
            boundary = StakeBoundary(min_stake, max_stake)
        except ValueError as e:
            print(f"  ✗ {e}"); return

        sp = SessionParameters(
            stop_loss_threshold   = stop_loss   if stop_loss   > 0 else None,
            take_profit_threshold = take_profit if take_profit > 0 else None,
            max_rounds            = max_rounds  if max_rounds  > 0 else None,
        )
        oc = OddsConfig(win_probability=win_prob, payout_multiplier=payout)
        prefs = BettingPreferences(
            strategy_type      = strategy_type,
            initial_stake      = initial_stake,
            stake_boundary     = boundary,
            session_parameters = sp,
            odds_config        = oc,
            strategy_param     = strategy_param,
        )

        # Start session
        try:
            session = self._session_mgr.start_session(gambler.id, session_name, prefs)
        except SessionAlreadyActiveError as e:
            print(f"  ✗ {e}"); return
        except GamblingAppError as e:
            print(f"  ✗ {e}"); return

        print(f"\n  ✅  Session #{session.id} started!")

        # Build strategy object
        strategy = self._build_strategy(strategy_type, initial_stake, boundary,
                                         strategy_param, win_prob)

        # Confirm run
        if not self._io.get_yes_no("\n  Run session now?"):
            print("  Session saved. Resume from Session History.")
            return

        # Run!
        print(banner("🎲  GAME RUNNING  🎲"))
        final_stats = self._engine.run_session(session, gambler, strategy, verbose=True)

        # Refresh gambler from DB then show summary
        gambler = self._gambler_svc.get_gambler(gambler.id)
        bets    = self._bet_svc.get_session_bets(session.id)
        session = self._session_mgr.get_session(session.id)
        SessionSummary.print_full(session, gambler, final_stats, bets)

    def _pick_strategy(self) -> Optional[StrategyType]:
        print(mini_banner("Choose Strategy"))
        strategies = [
            (1, StrategyType.MARTINGALE,           "Double on loss, reset on win"),
            (2, StrategyType.FIBONACCI,             "Fibonacci sequence on losses"),
            (3, StrategyType.FIXED,                 "Always bet the same amount"),
            (4, StrategyType.PERCENTAGE,            "% of current bankroll"),
            (5, StrategyType.RANDOM_OUTCOME,        "Random bet within bounds"),
            (6, StrategyType.WEIGHTED_PROBABILITY,  "Weighted by win probability"),
        ]
        for n, st, desc in strategies:
            print(f"  {n}. {st.value:<25} – {desc}")
        choice = self._io.get_menu_choice("  Strategy: ", range(1, 7))
        if choice is None:
            return None
        return strategies[choice - 1][1]

    @staticmethod
    def _build_strategy(st: StrategyType, base: Decimal, boundary: StakeBoundary,
                         param: Optional[Decimal], win_prob: float):
        if st == StrategyType.MARTINGALE:
            return MartingaleStrategy(base, boundary)
        if st == StrategyType.FIBONACCI:
            return FibonacciStrategy(base, boundary)
        if st == StrategyType.FIXED:
            return FixedStrategy(base, boundary)
        if st == StrategyType.PERCENTAGE:
            pct = param if param else Decimal("0.05")
            return PercentageStrategy(base, boundary, pct)
        if st == StrategyType.RANDOM_OUTCOME:
            return RandomOutcomeStrategy(base, boundary)
        if st == StrategyType.WEIGHTED_PROBABILITY:
            return WeightedProbabilityStrategy(base, boundary, float(win_prob))
        raise ValueError(f"Unknown strategy: {st}")

    # ════════════════════════════════════════════════════════════════════════
    # SESSION HISTORY
    # ════════════════════════════════════════════════════════════════════════

    def _session_history_flow(self) -> None:
        gid = self._io.get_int("  Gambler ID: ", 1)
        if gid is None:
            return
        try:
            gambler = self._gambler_svc.get_gambler(gid)
        except GamblerNotFoundError as e:
            print(f"  ✗ {e}"); return

        sessions = self._session_mgr.get_all_sessions(gambler.id)
        if not sessions:
            print("  No sessions found."); return

        print(mini_banner(f"Sessions for {gambler.username}"))
        for s in sessions:
            stats = self._session_mgr.get_stats(s.id)
            if stats:
                SessionSummary.print_brief(s, stats)
            else:
                print(f"  [{s.id}] {s.session_name}  (no stats yet)")

        # Drill into one?
        sid = self._io.get_int("\n  Enter Session ID for details (0 to skip): ", 0)
        if sid and sid > 0:
            self._show_session_detail(sid, gambler)

    def _show_session_detail(self, session_id: int, gambler) -> None:
        try:
            session = self._session_mgr.get_session(session_id)
            stats   = self._session_mgr.get_stats(session_id)
            bets    = self._bet_svc.get_session_bets(session_id)
            if stats:
                SessionSummary.print_full(session, gambler, stats, bets)
            else:
                print("  No statistics available for this session.")
        except GamblingAppError as e:
            print(f"  ✗ {e}")
