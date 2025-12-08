from discord import Message as DiscordMessage
from sqlmodel.ext.asyncio.session import AsyncSession
import structlog

from database import TicketChannel, engine
from handlers.chat_history_handler import MessageInput, ChatHistoryHandler
from handlers.debounce_handler import DebounceHandler

log = structlog.get_logger()


async def _trigger_agent_response(channel_id: int):
    """Placeholder for triggering the AI agent response."""
    log.info("Agent response triggered", channel_id=channel_id)
    # TODO: Implement actual agent response
    pass


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

        ticket_owner: bool = message.author.id == self.ticket_channel.user_id

        message_input = MessageInput(
            user_id=message.author.id,
            username=message.author.name,
            content=message.content,
            chat_role="ticket_owner" if ticket_owner else "support",
            # TODO does not support attachments yet
        )

        await chat.push(message_input, "user")

        if not ticket_owner:
            return

        debounce = DebounceHandler(
            channel_id=self.ticket_channel.id,
            on_ready=_trigger_agent_response,
        )

        await debounce.schedule()
