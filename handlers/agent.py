from litellm.types.utils import Message
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from handlers.knowledge import KnowledgeHandler
else:
    KnowledgeHandler = Any

MessageHistory = list[Message]


class AgentHandler:
    """Handles AI chat interactions."""

    def __init__(self, knowledge: KnowledgeHandler | None = None):
        self.knowledge = knowledge

    async def generate_response(
        self,
        user_message: Message,
        message_history: MessageHistory,
    ) -> str:
        pass
