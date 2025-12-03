from litellm.types.utils import Message

MessageHistory = list[Message]


class AIChatHandler:
    """Handles AI chat interactions."""

    async def generate_response(
        self,
        user_message: Message,
        message_history: MessageHistory,
    ) -> str:
        pass
