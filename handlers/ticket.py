from litellm.types.utils import Message


class TicketHandler:
    """Handles ticket creation and management."""

    async def open(
        self,
    ):
        pass

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
