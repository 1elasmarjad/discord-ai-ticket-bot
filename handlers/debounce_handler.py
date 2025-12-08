import asyncio
from typing import Awaitable, Callable

from litellm import acompletion
from litellm.types.utils import Message
import structlog

from handlers.chat_history_handler import ChatHistoryHandler

log = structlog.get_logger()

# Track pending response tasks per channel (channel_id -> asyncio.Task)
_pending_responses: dict[int, asyncio.Task] = {}

IDLE_CHECK_PROMPT = """You are analyzing a support ticket conversation to determine if the user has finished asking their question.

Review the recent messages and determine if the user appears to be DONE typing and ready for a response.

Return ONLY "yes" or "no":
- "yes" = The user has completed their question/message and is waiting for help
- "no" = The user indicated they will send more (e.g., "brb", "one sec", "let me check"), OR their message appears incomplete/cut off

Recent conversation:
{conversation}

Is the user done and ready for a response?"""

# Type alias for the response callback
ResponseCallback = Callable[[int], Awaitable[None]]


class DebounceHandler:
    """Handles debounced response scheduling for ticket channels."""

    def __init__(
        self,
        channel_id: int,
        on_ready: ResponseCallback,
        delay_seconds: float = 5.0,
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
                messages = await chat.fetch()

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
        conversation_text = "\n".join(f"{msg.role}: {msg.content}" for msg in recent)

        try:
            response = await acompletion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": IDLE_CHECK_PROMPT.format(
                            conversation=conversation_text
                        ),
                    }
                ],
            )

            answer = response.choices[0].message.content.strip().lower()
            is_done = answer == "yes"

            log.debug(
                "LLM idle check result",
                channel_id=self.channel_id,
                answer=answer,
                is_done=is_done,
            )

            return is_done
        except Exception as e:
            log.error(
                "Failed to check if user is done",
                channel_id=self.channel_id,
                error=str(e),
            )
            return False
