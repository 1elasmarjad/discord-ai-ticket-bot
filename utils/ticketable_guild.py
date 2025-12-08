from contextlib import asynccontextmanager
from typing import AsyncGenerator

from discord import Guild, CategoryChannel, Member, TextChannel
from sqlmodel.ext.asyncio.session import AsyncSession
from database import Guild as DatabaseGuild, TicketChannel, engine


def get_ticket_channel(channel_id: int) -> TextChannel | None:
    """Get a ticket channel by ID from the bot."""
    from main import bot

    channel = bot.get_channel(channel_id)
    if channel and isinstance(channel, TextChannel):
        return channel
    return None


async def send_ticket_message(channel_id: int, content: str) -> None:
    """Send a message to a ticket channel."""
    channel = get_ticket_channel(channel_id)
    if channel:
        await channel.send(content)


@asynccontextmanager
async def ticket_typing(channel_id: int) -> AsyncGenerator[None, None]:
    """Context manager to show typing indicator in a ticket channel.

    Usage:
        async with ticket_typing(channel_id):
            # do work while typing indicator is shown
            response = await generate_response()
    """
    channel = get_ticket_channel(channel_id)
    if channel:
        async with channel.typing():
            yield
    else:
        yield


class TicketableGuild:
    """A Discord guild that can have tickets."""

    def __init__(self, guild: Guild, database_guild: DatabaseGuild):
        self.guild = guild
        self.database_guild = database_guild

    @property
    def id(self) -> int:
        return self.guild.id

    async def get_category_channel(self) -> CategoryChannel | None:
        if self.database_guild.category_channel_id:
            return self.guild.get_channel(self.database_guild.category_channel_id)

        return None

    async def create_ticket_channel(self, *, suffix: str, user: Member) -> TextChannel:
        category: CategoryChannel | None = await self.get_category_channel()

        if not category:
            raise ValueError("No available category channel found")

        channel: TextChannel = await category.create_text_channel(f"ticket-{suffix}")

        await channel.set_permissions(
            user,
            view_channel=True,
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True,
        )

        return channel

    async def close_ticket_channel(self, *, channel: TextChannel):
        async with AsyncSession(engine) as session:
            ticket = await session.get(TicketChannel, channel.id)

            if not ticket:
                raise ValueError(f"Ticket channel {channel.id} not found in database")

            user = self.guild.get_member(ticket.user_id)

            if not user:
                raise ValueError(f"User {ticket.user_id} not found in guild")

            await channel.set_permissions(user, overwrite=None)

    @classmethod
    async def load(cls, guild: Guild, session: AsyncSession) -> "TicketableGuild":
        db_guild: DatabaseGuild | None = await session.get(DatabaseGuild, guild.id)

        if not db_guild:
            raise ValueError(f"Guild {guild.id} not found in database")

        return cls(guild=guild, database_guild=db_guild)
