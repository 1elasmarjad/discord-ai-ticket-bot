import discord
from discord import Bot
from settings import settings
import structlog
from rich.console import Console
from datetime import datetime

log = structlog.get_logger()
console = Console()

bot = discord.Bot()

_spinner = None


def get_log_prefix():
    """Generate a structlog-style prefix with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[dim]{timestamp}[/]"


@bot.event
async def on_ready():
    global _spinner
    if _spinner:
        _spinner.stop()
        _spinner = None
    log.info(f"{bot.user} is ready and online!", dev_mode=settings.dev_mode)


def load_cogs(bot: Bot):
    bot.load_extension("commands.development")


if __name__ == "__main__":
    load_cogs(bot)

    log.info("Cogs loaded")

    _spinner = console.status(f"{get_log_prefix()} Starting bot...", spinner="dots")
    _spinner.start()

    bot.run(settings.discord_bot_token)
