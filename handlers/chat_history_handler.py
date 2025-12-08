from typing import Literal
from litellm.types.utils import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel
from database import engine, TicketChannel
import structlog

log = structlog.get_logger()


class MessageInput(BaseModel):
    chat_role: Literal["support", "ticket_owner"]
    user_id: int
    username: str
    content: str
    attachment_data: bytes | None = None


class ChatHistoryHandler:
    """Handles the chat history for a given ticket."""

    def __init__(self, ticket_channel_id: int):
        self.ticket_channel_id = ticket_channel_id

    async def push(self, message: MessageInput, role: Literal["assistant", "user"]):
        raw_json: str = message.model_dump_json()

        msg = Message(
            content=raw_json,
            role=role,
        )

        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(TicketChannel).where(
                        TicketChannel.id == self.ticket_channel_id
                    )
                )

                ticket = result.scalars().one()
                ticket.messages = ticket.messages + [msg.model_dump()]

        log.debug(
            "Pushed message to ticket channel",
            ticket_channel_id=self.ticket_channel_id,
            message=msg.model_dump(),
        )

    async def fetch(self) -> list[Message]:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(TicketChannel).where(TicketChannel.id == self.ticket_channel_id)
            )
            ticket = result.scalars().one()
            return [Message(**msg) for msg in ticket.messages]
