"""AgriScore AI agent — supports Claude (Bedrock/API) and OpenAI-compatible providers.

Provider is selected via LLM_PROVIDER env var:
  bedrock   → Claude via AWS Bedrock (default, IAM auth)
  anthropic → Claude via direct API
  openai    → OpenAI
  groq      → Groq (Llama, OpenAI-compatible)

Model is selected via LLM_MODEL env var, or uses the provider default.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import TOOL_DEFINITIONS, execute_tool
from app.config import settings
from app.llm import active_model, get_claude_client, get_groq_client, get_openai_client
from app.models.database import Conversation, Farmer, MessageRole, MessageType

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 5


def _openai_tools() -> list[dict]:
    """Convert Anthropic-style tool definitions to OpenAI function format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in TOOL_DEFINITIONS
    ]


async def _run_anthropic_loop(
    history: list[dict],
    user_text: str,
    phone: str,
    db: AsyncSession,
) -> str:
    """Anthropic agent loop (works for both Bedrock and direct API).

    history is plain [{role, content}] text messages.
    """
    client = get_claude_client()
    model = active_model()
    # XML-tag user content for prompt injection mitigation
    tagged_text = f"<user_message>{user_text}</user_message>"
    messages = list(history) + [{"role": "user", "content": tagged_text}]

    for round_num in range(MAX_TOOL_ROUNDS):
        logger.info("Claude agent round %d for %s (model=%s)", round_num + 1, phone, model)

        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("Tool call: %s(%s)", block.name, block.input)
                    result_text = await execute_tool(block.name, block.input, phone, db)
                    logger.info("Tool result: %s", result_text[:100])
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        }
                    )

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            return "".join(block.text for block in response.content if hasattr(block, "text"))
        else:
            logger.warning("Unexpected stop_reason: %s", response.stop_reason)
            return "Disculpa, hubo un problema. ¿Puedes intentar de nuevo?"

    return "Disculpa, el procesamiento tomó demasiado tiempo. ¿Puedes intentar de nuevo?"


async def _run_openai_loop(
    history: list[dict],
    user_text: str,
    phone: str,
    db: AsyncSession,
    client=None,
) -> str:
    """OpenAI-compatible agent loop (works for OpenAI and Groq).

    history is plain [{role, content}] text messages.
    """
    if client is None:
        client = get_openai_client()
    model = active_model()
    tagged_text = f"<user_message>{user_text}</user_message>"
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}] + list(history) + [{"role": "user", "content": tagged_text}]
    )
    tools = _openai_tools()

    for round_num in range(MAX_TOOL_ROUNDS):
        logger.info("OpenAI-compat agent round %d for %s (model=%s)", round_num + 1, phone, model)

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)

            for call in msg.tool_calls:
                tool_input = json.loads(call.function.arguments)
                logger.info("Tool call: %s(%s)", call.function.name, tool_input)
                result_text = await execute_tool(call.function.name, tool_input, phone, db)
                logger.info("Tool result: %s", result_text[:100])
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result_text,
                    }
                )

        else:
            return msg.content or "Disculpa, no pude generar una respuesta."

    return "Disculpa, el procesamiento tomó demasiado tiempo. ¿Puedes intentar de nuevo?"


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

    # Load conversation history — last 20 messages, plain text only
    result = await db.execute(
        select(Conversation)
        .where(Conversation.farmer_id == farmer.id)
        .order_by(Conversation.timestamp.desc())
        .limit(20)
    )
    history = [{"role": row.role.value, "content": row.content} for row in reversed(result.scalars().all())]

    # Save incoming user message
    db.add(
        Conversation(
            farmer_id=farmer.id,
            role=MessageRole.user,
            content=user_text,
            message_type=MessageType(message_type) if message_type in MessageType.__members__ else MessageType.text,
        )
    )
    await db.commit()

    # Dispatch to provider loop
    provider = settings.llm_provider
    logger.info("Running agent with provider=%s model=%s", provider, active_model())

    if provider in ("groq",):
        final_text = await _run_openai_loop(history, user_text, phone, db, client=get_groq_client())
    elif provider == "openai":
        final_text = await _run_openai_loop(history, user_text, phone, db, client=get_openai_client())
    else:
        # "bedrock" and "anthropic" both use the Anthropic SDK
        final_text = await _run_anthropic_loop(history, user_text, phone, db)

    # Save assistant response
    if final_text:
        db.add(
            Conversation(
                farmer_id=farmer.id,
                role=MessageRole.assistant,
                content=final_text,
                message_type=MessageType.text,
            )
        )
        await db.commit()

    return final_text
