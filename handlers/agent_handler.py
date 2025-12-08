from litellm import acompletion
from litellm.types.utils import Message
from typing import TYPE_CHECKING, Any
import structlog

if TYPE_CHECKING:
    from handlers.knowledge_handler import KnowledgeHandler
else:
    KnowledgeHandler = Any

log = structlog.get_logger()

MessageHistory = list[Message]

SYSTEM_PROMPT = """You are a helpful and friendly support assistant. Your role is to assist users with their questions and issues.

Guidelines:
- Be concise but thorough in your responses
- If you don't know something, say so honestly
- Be patient and understanding with users
- Ask clarifying questions if the user's request is unclear
- Provide step-by-step instructions when appropriate"""


class AgentHandler:
    """Handles AI chat interactions."""

    def __init__(self, knowledge: KnowledgeHandler | None = None):
        self.knowledge = knowledge

    async def generate_response(self, message_history: MessageHistory) -> str:
        """Generate an AI response based on the conversation history."""
        messages: list[Message] = [Message(content=SYSTEM_PROMPT, role="system")]
        messages.extend([msg.model_dump() for msg in message_history])

        log.debug("Generating agent response", message_count=len(message_history))

        response = await acompletion(
            model="openrouter/openai/gpt-4o-mini",
            messages=messages,
        )

        content = response.choices[0].message.content
        log.debug("Agent response generated", response_length=len(content))

        return content
