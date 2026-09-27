import os
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

hindsight = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

BANK_ID = "hackathon-agent"


def ask_agent(user_message):

    # 1. Recall relevant memories from Hindsight
    result = hindsight.recall(
        bank_id=BANK_ID,
        query=user_message,
        budget="high"
    )

    # 2. Sort memories by when they were stored
    memories_list = list(result.results)

    memories_list.sort(
        key=lambda memory: memory.mentioned_at
        if memory.mentioned_at
        else datetime.min,
        reverse=True
    )

    # 3. Build memory context
    memories = "\n".join(
        f"- {memory.text} "
        f"(stored: {memory.mentioned_at})"
        for memory in memories_list[:10]
    )

    # 4. Give the memories to Groq
    prompt = f"""
You are an AI agent with long-term memory.

CURRENT USER MESSAGE:
{user_message}

MEMORIES FROM HINDSIGHT:
{memories}

IMPORTANT RULES:

- Hindsight memories are ordered from newest to oldest.
- The newest explicit user preference is the current preference.
- If an older preference conflicts with a newer preference,
  ALWAYS follow the newer preference.
- Never choose an older preference just because it appears more often.
- For project-specific preferences, the newest project-specific
  preference has priority.
- Answer only what the user asked.
- Keep the answer concise.
- Do not invent information.

Now answer the current user message.
"""

    # 5. Generate answer
    response = groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    # 6. Detect preference updates
    lower_message = user_message.lower()

    preference_phrases = [
        "i prefer",
        "i like",
        "my favorite",
        "i don't like",
        "i changed my preference",
        "i now prefer",
        "for this project",
        "i want to use"
    ]

    if any(phrase in lower_message for phrase in preference_phrases):

        hindsight.retain(
            bank_id=BANK_ID,
            content=f"""
CURRENT USER PREFERENCE UPDATE:

The user explicitly stated:
{user_message}

This is a new preference.
If it conflicts with an older preference,
this newer preference should be treated as current.
"""
        )

    # 7. Store complete interaction
    hindsight.retain(
        bank_id=BANK_ID,
        content=f"""
User interaction:

User: {user_message}

Assistant: {answer}
"""
    )

    return answer