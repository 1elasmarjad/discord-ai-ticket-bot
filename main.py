import discord
from discord import Bot
from settings import settings
import structlog

log = structlog.get_logger()

bot = discord.Bot()


@bot.event
async def on_ready():
    log.info(f"{bot.user} is ready and online!", dev_mode=settings.dev_mode)


def load_cogs(bot: Bot):
    bot.load_extension("commands.development")


if __name__ == "__main__":
    load_cogs(bot)

    log.info("Cogs loaded")

    bot.run(settings.discord_bot_token)
