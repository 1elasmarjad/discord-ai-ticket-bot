import discord


class CloseTicketEmbed(discord.Embed):
    """Embed shown in ticket channel with close button."""

    def __init__(self):
        super().__init__(
            title="🔒 Close Ticket",
            description="Click the button below to close this ticket.\n\nOnce closed, you will no longer be able to view this channel.",
            color=discord.Colour.orange(),
        )


class CloseTicketConfirmEmbed(discord.Embed):
    """Embed shown for close ticket confirmation."""

    def __init__(self):
        super().__init__(
            title="⚠️ Confirm Close Ticket",
            description="Are you sure you want to close this ticket?\n\nThis action cannot be undone.",
            color=discord.Colour.orange(),
        )


class TicketClosedEmbed(discord.Embed):
    """Embed sent when a ticket is closed."""

    def __init__(self):
        super().__init__(
            title="🔒 Ticket Closed",
            description="This ticket has been closed.\n\nThank you for contacting support!",
            color=discord.Colour.red(),
        )


class TicketClosedDMEmbed(discord.Embed):
    """Embed sent as DM to ticket opener when ticket is closed."""

    def __init__(self, ticket_channel_mention: str, closed_by_user: bool):
        if closed_by_user:
            description = f"Your ticket {ticket_channel_mention} has been closed.\n\nYou closed this ticket yourself."
        else:
            description = f"Your ticket {ticket_channel_mention} has been closed by staff.\n\nThank you for contacting support!"

        super().__init__(
            title="🔒 Ticket Closed",
            description=description,
            color=discord.Colour.red(),
        )
