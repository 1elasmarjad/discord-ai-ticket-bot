import discord
from discord.ui import View, Button
from discord import Interaction

from embeds.open_ticket import TicketCreatedEmbed
from handlers.ticket_handler import TicketHandler
from utils.ticketable_guild import TicketableGuild
from sqlmodel.ext.asyncio.session import AsyncSession
from database import engine


class OpenTicketView(View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        custom_id = f"open_ticket_{guild_id}"

        button = Button(
            label="Open Support Ticket",
            style=discord.ButtonStyle.green,
            emoji="🛎️",
            custom_id=custom_id,
        )
        button.callback = self.button_callback
        self.add_item(button)

    async def button_callback(self, interaction: Interaction):
        guild = interaction.guild

        async with AsyncSession(engine) as session:
            ticketable_guild = await TicketableGuild.create(guild, session)

        ticket_handler = TicketHandler(ticketable_guild)

        ticket_channel = await ticket_handler.open(user=interaction.user)

        ticket_embed = TicketCreatedEmbed(ticket_channel.mention)

        await interaction.response.send_message(embed=ticket_embed, ephemeral=True)

        try:
            await interaction.user.send(embed=ticket_embed)
        except discord.Forbidden:
            pass
