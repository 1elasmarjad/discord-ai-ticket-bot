from discord import Guild, CategoryChannel, Member, TextChannel
from sqlmodel.ext.asyncio.session import AsyncSession
from database import Guild as DatabaseGuild, engine


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

        return channel

    @classmethod
    async def create(cls, guild: Guild, session: AsyncSession) -> "TicketableGuild":
        db_guild: DatabaseGuild | None = await session.get(DatabaseGuild, guild.id)

        if not db_guild:
            raise ValueError(f"Guild {guild.id} not found in database")

        return cls(guild=guild, database_guild=db_guild)
