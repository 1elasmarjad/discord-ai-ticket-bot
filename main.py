import discord
from discord import Bot, Message
from handlers.message_ingest_handler import MessageIngestHandler
from settings import settings
import structlog
from rich.console import Console
from datetime import datetime
from views.open_ticket_view import OpenTicketView

log = structlog.get_logger()
console = Console()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(
    intents=intents,
)

_spinner = None


def get_log_prefix():
    """Generate a structlog-style prefix with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[dim]{timestamp}[/]"


def register_persistent_views(bot: Bot):
    """Register persistent views for all guilds the bot is in.

    This ensures buttons work even after bot restarts.
    """
    registered_guild_ids = set[int]()

    for guild in bot.guilds:
        if guild.id in registered_guild_ids:
            continue

        view = OpenTicketView(guild_id=guild.id)
        bot.add_view(view)
        registered_guild_ids.add(guild.id)

    log.info(
        "Persistent views registered",
        total_guilds=len(registered_guild_ids),
    )


@bot.event
async def on_ready():
    global _spinner
    if _spinner:
        _spinner.stop()
        _spinner = None
    log.info(f"{bot.user} is ready and online!", dev_mode=settings.dev_mode)

    register_persistent_views(bot)


@bot.event
async def on_error(event, *args, **kwargs):
    log.error(f"Error in {event}", exc_info=True)


@bot.event
async def on_message(message: Message):
    message_ingest = MessageIngestHandler()

    if await message_ingest.ignore(message):
        return

    await message_ingest.process(message)


def load_cogs(bot: Bot):
    if settings.dev_mode:
        bot.load_extension("commands.development")

    bot.load_extension("commands.setup")
    bot.load_extension("commands.spawn")


if __name__ == "__main__":
    load_cogs(bot)

    log.info("Cogs loaded")

    _spinner = console.status(f"{get_log_prefix()} Starting bot...", spinner="dots")
    _spinner.start()

    bot.run(settings.discord_bot_token)
