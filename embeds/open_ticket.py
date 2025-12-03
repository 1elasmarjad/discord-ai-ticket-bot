import discord


class OpenTicketEmbed(discord.Embed):
    """Embed for the ticket panel."""

    def __init__(self):
        super().__init__(
            title="🎫 Support Tickets",
            description="Need help? Click the button below to open a support ticket.\n\nOur team will assist you as soon as possible.",
            color=discord.Colour.blue(),
        )

        self.set_footer(text="We're here to help!")
