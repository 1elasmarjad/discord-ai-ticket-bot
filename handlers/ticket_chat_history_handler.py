from litellm.types.utils import Message


class TicketChatHistoryHandler:
    """Handles the chat history for a given ticket."""

    def __init__(self, ticket_channel_id: int):
        self.ticket_channel_id = ticket_channel_id

    async def push(self, message: Message):
        pass

    async def fetch(self) -> list[Message]:
        pass
