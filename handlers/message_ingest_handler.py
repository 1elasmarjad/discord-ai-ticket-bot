from discord import Message as DiscordMessage
from sqlmodel.ext.asyncio.session import AsyncSession
from database import TicketChannel, engine
from handlers.chat_history_handler import (
    MessageInput,
    RoleType,
    ChatHistoryHandler,
)


class MessageIngestHandler:
    def __init__(self):
        self.ticket_channel: TicketChannel | None = None

    async def ignore(self, message: DiscordMessage) -> bool:
        if message.author.bot:
            return True

        if not message.channel.name.startswith("ticket-"):
            return True

        # check if its in a ticket channel
        async with AsyncSession(engine) as session:
            self.ticket_channel = await session.get(TicketChannel, message.channel.id)

            if not self.ticket_channel:
                return True

        return False

    async def process(self, message: DiscordMessage):
        if not self.ticket_channel:
            return

        chat = ChatHistoryHandler(self.ticket_channel.id)

        message_input = MessageInput(
            user_id=message.author.id,
            username=message.author.name,
            content=message.content,
            # TODO does not support attachments yet
        )

        await chat.push(message_input, RoleType.USER)
