from sqlmodel.ext.asyncio.session import AsyncSession
from database import TicketChannel, engine
from utils.ticketable_guild import TicketableGuild
from litellm.types.utils import Message
from discord import TextChannel, Member


class TicketHandler:
    """Handles ticket creation and management."""

    def __init__(self, ticketable_guild: TicketableGuild):
        self.ticketable_guild = ticketable_guild

    async def open(self, *, user: Member):
        guild_id = self.ticketable_guild.database_guild.id

        async with AsyncSession(engine) as session:
            async with session.begin():
                max_number: int = await TicketChannel.get_largest_ticket_number(
                    session, guild_id
                )

                next_number = max_number + 1

                ticket = TicketChannel(
                    guild_id=guild_id, ticket_number=next_number, user_id=user.id
                )
                session.add(ticket)
                await session.flush()

                ticket_channel: TextChannel = (
                    await self.ticketable_guild.create_ticket_channel(
                        suffix=f"{next_number:04d}", user=user
                    )
                )

        return ticket_channel

    async def close(
        self,
    ):
        pass

    @property
    def chat(self) -> "TicketChatHistory":
        return TicketChatHistory(None)  # TODO: add the text channel id


class TicketChatHistory:
    def __init__(self, text_channel_id: int):
        self.text_channel_id = text_channel_id

    async def push(
        self,
        message: Message,
    ):
        pass

    async def fetch(
        self,
    ) -> list[Message]:
        pass
