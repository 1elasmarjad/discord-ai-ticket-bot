import discord
from discord.ui import View, Button
from discord import Interaction


class OpenTicketView(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(
        label="Open Support Ticket", style=discord.ButtonStyle.green, emoji="🛎️"
    )
    async def button_callback(self, button: Button, interaction: Interaction):
        await interaction.response.send_message("Button clicked!", ephemeral=True)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
