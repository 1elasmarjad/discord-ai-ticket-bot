import discord
from discord.ui import View, Button
from discord import Interaction


class OpenTicketView(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Click Me!", style=discord.ButtonStyle.primary, emoji="👍")
    async def button_callback(self, button: Button, interaction: Interaction):
        await interaction.response.send_message("Button clicked!", ephemeral=True)

    @discord.ui.button(label="Danger", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def danger_button(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(
            "Danger button pressed!", ephemeral=True
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
