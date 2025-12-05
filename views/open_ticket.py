import discord
from discord.ui import View, Button
from discord import Interaction


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
        await interaction.response.send_message("Button clicked!", ephemeral=True)
