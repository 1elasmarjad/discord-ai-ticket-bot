import discord
from discord import Bot, ApplicationContext
from discord.ext import commands


class Development(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.slash_command(name="hello", description="Say hello world!")
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond("Hello, World!")


def setup(bot: Bot):
    bot.add_cog(Development(bot))
