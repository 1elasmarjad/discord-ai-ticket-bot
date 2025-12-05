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


class TicketCreatedEmbed(discord.Embed):
    """Embed sent when a ticket is successfully created."""

    def __init__(self, ticket_channel_mention: str):
        super().__init__(
            title="🎫 Ticket Opened",
            description=(
                f"You just opened a ticket in {ticket_channel_mention}.\n\n"
                "A staff member will be with you shortly.\n"
                "Please explain your issue in the ticket channel while you wait!"
            ),
            color=discord.Colour.green(),
        )
