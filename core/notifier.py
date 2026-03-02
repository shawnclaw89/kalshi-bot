"""Send Telegram alerts via OpenClaw CLI."""
import subprocess, logging
log = logging.getLogger(__name__)

def send(message: str, to: str = "7591705971"):
    try:
        r = subprocess.run(
            ["openclaw","message","send","--channel","telegram","--target",to,"--message",message],
            capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            log.info("Alert sent.")
        else:
            log.error(f"Send failed: {r.stderr.strip()}")
    except FileNotFoundError:
        print(message)
    except Exception as e:
        log.error(f"Notifier: {e}")

def opportunity_alert(strategy, market, detail, url=""):
    lines = [f"💡 *{strategy}*", market, detail]
    if url: lines.append(f"🔗 {url}")
    send("\n".join(lines))

def trade_alert(strategy, action, market, price_cents, size_usd, paper=True, url=""):
    mode = "📝 PAPER" if paper else "🔴 LIVE"
    lines = [
        f"{mode} | *{strategy}*",
        f"{'🟢 BUY' if action=='buy' else '🔴 SELL'} {market}",
        f"Price: {price_cents}¢ (${price_cents/100:.2f}) | Size: ${size_usd:.2f}",
    ]
    if url: lines.append(f"🔗 {url}")
    send("\n".join(lines))
