# Kalshi Bot 🤖

Modular, US-legal prediction market trading bot for Kalshi. Paper trading by default, live when you're ready.

## Quick Start

```bash
pip3 install -r requirements.txt

# 1. Generate your API keys
python3 bot.py --setup-keys

# 2. Upload kalshi_public_key.pem to kalshi.com → Settings → API Keys
#    Copy the Key ID shown and paste into config.yaml as api_key_id

# 3. Test in paper mode (no real orders)
python3 bot.py --once

# 4. Check what it found
python3 bot.py --status

# 5. Run continuously
python3 bot.py
```

## Setting Up API Access (one-time)

Kalshi uses RSA key authentication — more secure than a password.

1. Run `python3 bot.py --setup-keys`
   - Creates `kalshi_private_key.pem` (keep secret — never share or commit)
   - Creates `kalshi_public_key.pem` (safe to share)

2. Go to **https://kalshi.com → Settings → API Keys**
   - Click **Create API Key**
   - Upload `kalshi_public_key.pem`
   - Copy the **Key ID** shown

3. Edit `config.yaml`:
   ```yaml
   api_key_id: "your-key-id-here"
   private_key_path: "kalshi_private_key.pem"
   ```

4. When ready to go live:
   ```yaml
   paper_trading: false
   ```

## Architecture

```
bot.py                      ← entry point
config.yaml                 ← toggle strategies, set thresholds, go live
core/
  api.py                    ← Kalshi REST API client
  auth.py                   ← RSA key setup + key generation
  engine.py                 ← main loop
  notifier.py               ← Telegram alerts via OpenClaw
  state.py                  ← positions, P&L, trade log
strategies/
  base.py                   ← BaseStrategy (inherit to add new strategies)
  endgame_arb.py            ← buy near-certain markets
  intramarket_arb.py        ← YES + NO < 100¢ arb
  momentum.py               ← trend following
```

## Adding a New Strategy

```python
# strategies/my_strategy.py
from strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    name = "my_strategy"

    def scan(self, markets, state, cfg, paper_trading):
        for m in markets:
            yes_ask = m.get("yes_ask", 0)  # price in CENTS (0-100)
            # your logic here
```

Register in `core/engine.py` + add config block in `config.yaml`. Done.

## Key Difference: Prices are in CENTS

Kalshi prices are **0–100 cents** (not 0–1 fractions like Polymarket).
- `yes_ask = 95` means YES costs 95¢ ($0.95)
- At resolution YES pays 100¢ ($1.00)
- Profit = 5¢ per contract

## Risk Controls

Edit in `config.yaml` under `risk:`:

| Setting | Default | Description |
|---|---|---|
| `max_open_positions` | 10 | Max simultaneous positions |
| `max_total_exposure_usd` | $200 | Max capital at risk |
| `max_daily_loss_usd` | $50 | Halt bot at this daily loss |
| `stop_loss_pct` | 30% | Exit position if down this % |
