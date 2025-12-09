import asyncio
import json
from typing import Awaitable, Callable

from litellm import acompletion
from litellm.types.utils import Message
from pydantic import BaseModel
import structlog

from handlers.chat_history_handler import ChatHistoryHandler

log = structlog.get_logger()

# Track pending response tasks per channel (channel_id -> asyncio.Task)
_pending_responses: dict[int, asyncio.Task] = {}

IDLE_CHECK_PROMPT = """You are analyzing a support ticket conversation to determine if the user has finished asking their question.

Review the recent messages and determine if the user appears to be DONE typing and ready for a response.

You will receive:
- The full recent conversation in this ticket.
- Messages may be from "user" (the person asking for help) or "agent/bot" (the support side).
- Messages are in order from oldest to newest.

Focus on the messages from the user in need of support.

Decide if the user seems:
- **DONE**: they've finished their thought / question and it's a good time for the bot to answer.
- **NOT_DONE**: they're still typing, adding context, or clearly not finished.

Return your decision in JSON format with two fields:
{
  "reasoning": "brief explanation of your decision",
  "user_finished": true or false
}
"""


class LLMResponseFormat(BaseModel):
    reasoning: str
    user_finished: bool


ResponseCallback = Callable[[int], Awaitable[None]]


class DebounceHandler:
    """Handles debounced response scheduling for ticket channels."""

    def __init__(
        self,
        channel_id: int,
        on_ready: ResponseCallback,
        delay_seconds: float = 1.0,
    ):
        self.channel_id = channel_id
        self.on_ready = on_ready
        self.delay_seconds = delay_seconds

    async def schedule(self):
        """Schedule a debounced response check. Cancels any existing pending task."""
        if self.channel_id in _pending_responses:
            _pending_responses[self.channel_id].cancel()
            log.debug("Cancelled pending response task", channel_id=self.channel_id)

        async def debounced_response():
            try:
                await asyncio.sleep(self.delay_seconds)

                # Fetch chat history and check if user is done
                chat = ChatHistoryHandler(self.channel_id)
                messages: list[Message] = await chat.fetch()

                if await self._check_if_user_done(messages):
                    await self.on_ready(self.channel_id)

            except asyncio.CancelledError:
                # Task was cancelled because user sent another message
                pass
            finally:
                _pending_responses.pop(self.channel_id, None)

        task = asyncio.create_task(debounced_response())
        _pending_responses[self.channel_id] = task

    async def _check_if_user_done(self, messages: list[Message]) -> bool:
        """Use LLM to determine if the user has finished typing their question."""
        if not messages:
            return False

        recent = messages[-5:]
        system_prompt = Message(content=IDLE_CHECK_PROMPT, role="system")
        messages = [system_prompt] + recent

        try:
            response = await acompletion(
                model="openrouter/openai/gpt-4o-mini",
                messages=messages,
                response_format=LLMResponseFormat,
            )

            message = response.choices[0].message

            log.debug(
                "LLM idle check result",
                channel_id=self.channel_id,
                response=message,
            )

            content_json = json.loads(message.content)
            return content_json.get("user_finished", False)

        except Exception as e:
            log.error(
                "Failed to check if user is done",
                channel_id=self.channel_id,
                error=str(e),
            )
            return False
