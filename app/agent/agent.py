"""AgriScore AI agent — Anthropic SDK with function calling."""

import logging
from datetime import datetime, timezone

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import TOOL_DEFINITIONS, execute_tool
from app.models.database import Farmer, Conversation, MessageRole, MessageType

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 5
MODEL = "claude-sonnet-4-5-20250929"

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def run_agent(
    phone: str,
    user_text: str,
    message_type: str,
    db: AsyncSession,
) -> str:
    """Run the agent loop for a single user message. Returns the final text response."""

    # Ensure farmer exists
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        farmer = Farmer(phone=phone)
        db.add(farmer)
        await db.commit()
        await db.refresh(farmer)

    # Load conversation history (last 20 messages for context window)
    result = await db.execute(
        select(Conversation)
        .where(Conversation.farmer_id == farmer.id)
        .order_by(Conversation.timestamp.desc())
        .limit(20)
    )
    history_rows = list(reversed(result.scalars().all()))

    # Build messages list for Anthropic API
    messages = []
    for row in history_rows:
        messages.append({"role": row.role.value, "content": row.content})

    # Add current user message
    messages.append({"role": "user", "content": user_text})

    # Save user message to DB
    db.add(Conversation(
        farmer_id=farmer.id,
        role=MessageRole.user,
        content=user_text,
        message_type=MessageType(message_type) if message_type in MessageType.__members__ else MessageType.text,
    ))
    await db.commit()

    # Agent loop with tool calling
    final_text = ""
    for round_num in range(MAX_TOOL_ROUNDS):
        logger.info("Agent round %d for %s", round_num + 1, phone)

        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Check if the model wants to use tools
        if response.stop_reason == "tool_use":
            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Process all tool calls in this response
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("Tool call: %s(%s)", block.name, block.input)
                    result_text = await execute_tool(
                        tool_name=block.name,
                        tool_input=block.input,
                        phone=phone,
                        db=db,
                    )
                    logger.info("Tool result: %s", result_text[:100])
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })

            # Send tool results back
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Extract final text response
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            break
        else:
            logger.warning("Unexpected stop_reason: %s", response.stop_reason)
            final_text = "Disculpa, hubo un problema. ¿Puedes intentar de nuevo?"
            break
    else:
        # Exhausted tool rounds
        final_text = "Disculpa, el procesamiento tomó demasiado tiempo. ¿Puedes intentar de nuevo?"

    # Save assistant response to DB
    if final_text:
        db.add(Conversation(
            farmer_id=farmer.id,
            role=MessageRole.assistant,
            content=final_text,
            message_type=MessageType.text,
        ))
        await db.commit()

    return final_text
