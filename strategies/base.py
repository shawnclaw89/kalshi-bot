"""Base class for all Kalshi strategies."""
from abc import ABC, abstractmethod
import logging
from core import state as state_mgr

class BaseStrategy(ABC):
    name: str = "unnamed"

    def __init__(self):
        self.log = logging.getLogger(f"strategy.{self.name}")

    @abstractmethod
    def scan(self, markets: list, state: dict, cfg: dict, paper_trading: bool):
        """
        Called each tick.
        markets: list of Kalshi market dicts (prices in CENTS 0-100)
        state:   shared mutable state
        cfg:     this strategy's config block
        paper_trading: True = simulate only
        """
        ...

    def market_url(self, ticker: str) -> str:
        from core.api import market_url
        return market_url(ticker)

    def is_already_open(self, state, ticker):
        return ticker in state.get("positions", {})

    def can_open(self, state, risk, size_usd):
        if state_mgr.position_count(state) >= risk.get("max_open_positions", 10):
            self.log.debug("Max positions reached.")
            return False
        if state_mgr.total_exposure(state) + size_usd > risk.get("max_total_exposure_usd", 200):
            self.log.debug("Max exposure reached.")
            return False
        if state.get("daily_pnl", 0) <= -risk.get("max_daily_loss_usd", 50):
            self.log.warning("Daily loss limit hit.")
            return False
        return True
