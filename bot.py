#!/usr/bin/env python3
"""
Kalshi Bot — Entry Point

Usage:
  python3 bot.py              # Run continuously
  python3 bot.py --once       # Single scan (for testing)
  python3 bot.py --status     # Show positions + P&L
  python3 bot.py --setup-keys # Generate RSA key pair for API auth
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(__file__))

def cmd_run(once=False):
    from core.engine import run
    run(once=once)

def cmd_status():
    from core import state as state_mgr
    state = state_mgr.load()
    print(f"\n{'='*50}\n  Kalshi Bot — Status\n{'='*50}")
    print(f"  Open positions : {state_mgr.position_count(state)}")
    print(f"  Total exposure : ${state_mgr.total_exposure(state):.2f}")
    print(f"  Daily P&L      : ${state.get('daily_pnl', 0):.2f}")
    print(f"  Total P&L      : ${state.get('total_pnl', 0):.2f}")
    print(f"  Daily trades   : {state.get('daily_trades', 0)}")
    print(f"  Last updated   : {state.get('last_updated', 'never')}")
    positions = state.get("positions", {})
    if positions:
        print("\n  Open Positions:")
        for ticker, pos in positions.items():
            print(f"    [{pos['strategy']}] {ticker}")
            print(f"      {pos['side']} @ {pos['entry_cents']}¢ | ${pos['size_usd']:.2f}")
    print()

def cmd_setup_keys():
    from core.auth import generate_keys
    generate_keys()

def main():
    p = argparse.ArgumentParser(description="Kalshi Trading Bot")
    p.add_argument("--once",       action="store_true", help="Run one scan then exit")
    p.add_argument("--status",     action="store_true", help="Show status and exit")
    p.add_argument("--setup-keys", action="store_true", help="Generate RSA key pair")
    args = p.parse_args()

    if args.setup_keys:    cmd_setup_keys()
    elif args.status:      cmd_status()
    elif args.once:        cmd_run(once=True)
    else:                  cmd_run(once=False)

if __name__ == "__main__":
    main()
