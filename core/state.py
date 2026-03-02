"""Persistent state — positions, P&L, trade log."""
import json, os
from datetime import datetime, timezone

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state.json")

def _default():
    return {"positions": {}, "daily_pnl": 0.0, "daily_trades": 0,
            "total_pnl": 0.0, "trade_log": [], "last_updated": None}

def load():
    if not os.path.exists(STATE_FILE):
        return _default()
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
        for k, v in _default().items():
            data.setdefault(k, v)
        return data
    except Exception:
        return _default()

def save(state):
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def open_position(state, ticker, strategy, side, entry_cents, size_usd):
    state["positions"][ticker] = {
        "strategy": strategy, "side": side,
        "entry_cents": entry_cents, "size_usd": size_usd,
        "opened_at": datetime.now(timezone.utc).isoformat(),
    }
    _log(state, "open", strategy, ticker, side, entry_cents, size_usd)

def close_position(state, ticker, exit_cents):
    pos = state["positions"].pop(ticker, None)
    if pos:
        pnl = ((exit_cents - pos["entry_cents"]) / pos["entry_cents"]) * pos["size_usd"]
        state["daily_pnl"] += pnl
        state["total_pnl"] += pnl
        _log(state, "close", pos["strategy"], ticker, pos["side"], exit_cents, pos["size_usd"], pnl)
        return pnl
    return 0.0

def _log(state, action, strategy, ticker, side, price, size_usd, pnl=None):
    state["daily_trades"] += 1
    state["trade_log"].append({
        "action": action, "strategy": strategy, "ticker": ticker,
        "side": side, "price_cents": price, "size_usd": size_usd,
        "pnl": pnl, "at": datetime.now(timezone.utc).isoformat(),
    })
    if len(state["trade_log"]) > 1000:
        state["trade_log"] = state["trade_log"][-1000:]

def total_exposure(state):
    return sum(p["size_usd"] for p in state["positions"].values())

def position_count(state):
    return len(state["positions"])
