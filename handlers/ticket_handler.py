from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from database import TicketChannel, engine
from utils.ticketable_guild import TicketableGuild
from discord import TextChannel, Member


class TicketHandler:
    """Handles ticket creation and management."""

    def __init__(self, guild: TicketableGuild):
        self.guild = guild

    async def open_ticket(self, *, user: Member):
        guild_id = self.guild.id

        async with AsyncSession(engine) as session:
            async with session.begin():
                max_number: int = await TicketChannel.get_largest_ticket_number(
                    session, guild_id
                )

                next_number = max_number + 1

                ticket_channel: TextChannel = await self.guild.create_ticket_channel(
                    suffix=f"{next_number:04d}", user=user
                )

                ticket = TicketChannel(
                    id=ticket_channel.id,
                    guild_id=guild_id,
                    ticket_number=next_number,
                    user_id=user.id,
                )

                session.add(ticket)

        return ticket_channel

    async def close_ticket(
        self,
        *,
        channel: TextChannel,
    ):
        async with AsyncSession(engine) as session:
            async with session.begin():
                ticket = await session.get(TicketChannel, channel.id)

                if not ticket:
                    raise ValueError(
                        f"Ticket channel {channel.id} not found in database"
                    )

                ticket.closed_at = datetime.now()
                session.add(ticket)

        await self.guild.close_ticket_channel(channel=channel)
