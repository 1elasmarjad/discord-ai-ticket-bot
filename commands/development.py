import discord
from discord import Bot, ApplicationContext
from discord.ext import commands
from components.open_ticket import OpenTicketView
from embeds.open_ticket import OpenTicketEmbed


class Development(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.slash_command(name="hello", description="Say hello world!")
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond("Hello, World!")

    @discord.slash_command(name="button", description="Show a custom button component")
    async def show_button(self, ctx: ApplicationContext):
        view = OpenTicketView()
        await ctx.respond(embed=OpenTicketEmbed(), view=view)


def setup(bot: Bot):
    bot.add_cog(Development(bot))
