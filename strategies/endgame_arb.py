"""
Endgame Arb — Buy near-certain Kalshi markets before they resolve at 100¢.
Prices are in cents. YES @ 96¢ → resolves at 100¢ = +4.2% guaranteed.
"""
from strategies.base import BaseStrategy
from core import api, notifier, state as state_mgr


class EndgameArbStrategy(BaseStrategy):
    name = "endgame_arb"

    def scan(self, markets, state, cfg, paper_trading):
        min_yes  = cfg.get("min_yes_price", 95)     # cents
        max_yes  = cfg.get("max_yes_price", 99)     # cents
        min_vol  = cfg.get("min_volume_24h", 500)
        max_pos  = cfg.get("max_position_usd", 20)
        min_ret  = cfg.get("min_return_pct", 0.5) / 100
        risk     = state.get("_risk_config", {})

        opps = []
        for m in markets:
            ticker   = m.get("ticker", "")
            title    = m.get("title", "")
            yes_ask  = m.get("yes_ask", 0)   # cheapest you can buy YES
            vol      = m.get("volume_24h", 0)

            if not (min_yes <= yes_ask <= max_yes):
                continue
            if vol < min_vol:
                continue
            if self.is_already_open(state, ticker):
                continue

            expected_ret = (100 - yes_ask) / yes_ask
            if expected_ret < min_ret:
                continue

            opps.append({
                "ticker": ticker, "title": title,
                "yes_ask": yes_ask,
                "ret_pct": round(expected_ret * 100, 2),
                "vol": vol,
            })

        opps.sort(key=lambda x: x["ret_pct"], reverse=True)

        for opp in opps[:3]:
            if not self.can_open(state, risk, max_pos):
                break

            contracts = api.usd_to_contracts(max_pos, opp["yes_ask"])
            url = self.market_url(opp["ticker"])
            detail = (
                f"YES @ {opp['yes_ask']}¢ → resolves 100¢\n"
                f"Return: +{opp['ret_pct']:.2f}% | Contracts: {contracts}\n"
                f"24h Vol: {opp['vol']:,}"
            )

            self.log.info(f"[{'PAPER' if paper_trading else 'LIVE'}] "
                          f"{opp['title'][:60]} | YES@{opp['yes_ask']}¢ | +{opp['ret_pct']:.2f}%")
            notifier.opportunity_alert("Endgame Arb 🎯", opp["title"][:80], detail, url)

            if paper_trading:
                state_mgr.open_position(state, opp["ticker"], self.name,
                                        "YES", opp["yes_ask"], max_pos)
            else:
                api.place_order(opp["ticker"], "yes", contracts, opp["yes_ask"])
                state_mgr.open_position(state, opp["ticker"], self.name,
                                        "YES", opp["yes_ask"], max_pos)
