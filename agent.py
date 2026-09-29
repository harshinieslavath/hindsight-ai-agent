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


# Store project-specific context
def remember_project_context(project_name, context):
    hindsight.retain(
        bank_id=BANK_ID,
        content=f"""
PROJECT CONTEXT:

Project: {project_name}

Context:
{context}

This information belongs specifically to this project
and should be used when answering future questions
about the project.
"""
    )


def ask_agent(user_message):

    lower_message = user_message.lower()

    # Check whether this is a preference question
    preference_question = any(
        phrase in lower_message
        for phrase in [
            "what do i prefer",
            "what framework do i prefer",
            "which framework do i prefer",
            "my current preference",
            "what is my preference",
            "what do i currently prefer",
            "which do i currently prefer"
        ]
    )

    # Recall relevant memories
    if preference_question:
        result = hindsight.recall(
            bank_id=BANK_ID,
            query=f"""
Current user preference for this project.
Latest framework preference.
{user_message}
""",
            budget="high"
        )
    else:
        result = hindsight.recall(
            bank_id=BANK_ID,
            query=user_message,
            budget="high"
        )

    memories_list = list(result.results)

    # Sort newest first
    memories_list.sort(
        key=lambda memory: memory.mentioned_at
        if memory.mentioned_at
        else datetime.min,
        reverse=True
    )

    # Keep only the newest 3 memories
    used_memories = memories_list[:3]

    memories = "\n".join(
        f"- {memory.text} "
        f"(stored: {memory.mentioned_at})"
        for memory in used_memories
    )

    prompt = f"""
You are an AI agent with long-term memory.

CURRENT USER MESSAGE:
{user_message}

MEMORIES FROM HINDSIGHT:
{memories}

IMPORTANT RULES:

- Use the memories provided by Hindsight.
- For preference questions, the newest explicit user
  preference is the current preference.
- A newer preference overrides an older preference.
- Never choose an older preference over a newer preference.
- Do not treat an assistant-generated answer as a user preference.
- Only an explicit statement from the user can create
  or change a user preference.
- Do not invent information.
- For project-specific questions, use project-specific memories.
- Answer only what the user asked.
- Keep the answer concise.

Now answer the current user message.
"""

    # Generate answer
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

    # Detect explicit user preference statements
    preference_phrases = [
        "i prefer",
        "i like",
        "my favorite",
        "i don't like",
        "i changed my preference",
        "i now prefer",
        "for this project",
        "i want to use",
        "my current preference"
    ]

    is_preference_update = any(
        phrase in lower_message
        for phrase in preference_phrases
    )

    # Store ONLY the user's explicit preference
    if is_preference_update:
        hindsight.retain(
            bank_id=BANK_ID,
            content=f"""
CURRENT USER PREFERENCE UPDATE:

The user explicitly stated:
{user_message}

This is the newest user preference.
If it conflicts with an older preference,
this newer preference should be treated as current.

IMPORTANT:
This memory represents the USER'S explicit preference,
not the assistant's answer.
"""
        )

    # Store normal interaction only when it is NOT
    # a preference-related question.
    #
    # This prevents an incorrect assistant answer from
    # becoming a future preference memory.
    if not preference_question and not is_preference_update:
        hindsight.retain(
            bank_id=BANK_ID,
            content=f"""
User interaction:

User: {user_message}

Assistant: {answer}
"""
        )

    return {
        "answer": answer,
        "used_memories": [
            {
                "memory": memory.text,
                "mentioned_at": str(memory.mentioned_at)
                if memory.mentioned_at
                else "Previously remembered"
            }
            for memory in used_memories
        ]
    }