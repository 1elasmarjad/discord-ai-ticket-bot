import discord
from discord.ui import View, Button
from discord import Interaction, TextChannel

from embeds.close_ticket import (
    TicketClosedEmbed,
    CloseTicketConfirmEmbed,
    TicketClosedDMEmbed,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from database import engine, TicketChannel


class CloseTicketView(View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

        custom_id = f"close_ticket_{channel_id}"

        button = Button(
            label="Close Ticket",
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id=custom_id,
        )
        button.callback = self.button_callback
        self.add_item(button)

    async def button_callback(self, interaction: Interaction):
        # Show confirmation prompt
        await interaction.response.send_message(
            embed=CloseTicketConfirmEmbed(),
            view=CloseTicketConfirmView(
                channel=interaction.channel,
                original_message=interaction.message,
                original_view=self,
            ),
            ephemeral=True,
        )


class CloseTicketConfirmView(View):
    def __init__(
        self,
        channel: TextChannel,
        original_message: discord.Message,
        original_view: CloseTicketView,
    ):
        super().__init__(timeout=60)
        self.channel = channel
        self.original_message = original_message
        self.original_view = original_view

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_button(self, button: Button, interaction: Interaction):
        from handlers.ticket_handler import TicketHandler
        from utils.ticketable_guild import TicketableGuild

        guild = interaction.guild

        async with AsyncSession(engine) as session:
            ticketable_guild = await TicketableGuild.load(guild, session)

        ticket_handler = TicketHandler(ticketable_guild)

        async with AsyncSession(engine) as session:
            ticket = await session.get(TicketChannel, self.channel.id)
            if not ticket:
                raise ValueError(
                    f"Ticket channel {self.channel.id} not found in database"
                )
            opener_user_id = ticket.user_id

        await ticket_handler.close_ticket(channel=self.channel)

        await interaction.response.edit_message(
            embed=TicketClosedEmbed(),
            view=None,
        )

        # Send closed message in the channel
        await self.channel.send(embed=TicketClosedEmbed())

        # Disable the original close button
        self.original_view.children[0].disabled = True
        await self.original_message.edit(view=self.original_view)

        opener = guild.get_member(opener_user_id)
        if opener:
            closed_by_user = interaction.user.id == opener_user_id
            dm_embed = TicketClosedDMEmbed(self.channel.mention, closed_by_user)

            try:
                await opener.send(embed=dm_embed)
            except discord.Forbidden:
                pass

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, button: Button, interaction: Interaction):
        await interaction.response.edit_message(
            content="Ticket close cancelled.",
            embed=None,
            view=None,
        )
