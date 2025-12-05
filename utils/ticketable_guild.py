from discord import Guild, CategoryChannel, Member, TextChannel
from sqlmodel.ext.asyncio.session import AsyncSession
from database import Guild as DatabaseGuild, TicketChannel, engine

from embeds.close_ticket import CloseTicketEmbed
from views.close_ticket_view import CloseTicketView


class TicketableGuild:
    """A guild that can have tickets."""

    def __init__(self, guild: Guild, database_guild: DatabaseGuild):
        self.guild = guild
        self.database_guild = database_guild

    async def available_category_channel(self) -> CategoryChannel | None:
        if self.database_guild.category_channel_id:
            return self.guild.get_channel(self.database_guild.category_channel_id)
        return None

    async def create_ticket_channel(self, *, suffix: str, user: Member) -> TextChannel:
        category: CategoryChannel | None = await self.available_category_channel()

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

        await channel.send(
            embed=CloseTicketEmbed(),
            view=CloseTicketView(channel.id),
        )

        await channel.send(
            content=f"Hey {user.mention} I'm an AI assistant! I'll try my best to help you out\n\n\
Please **explain your issue** in the ticket channel while you wait for staff to assist you"
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

            # Remove permissions by setting overwrite to None
            await channel.set_permissions(user, overwrite=None)

    @classmethod
    async def create(cls, guild: Guild, session: AsyncSession) -> "TicketableGuild":
        db_guild: DatabaseGuild | None = await session.get(DatabaseGuild, guild.id)

        if not db_guild:
            raise ValueError(f"Guild {guild.id} not found in database")

        return cls(guild=guild, database_guild=db_guild)
