from fastapi import FastAPI
from agent import (
    ask_agent,
    remember_project_context,
    hindsight,
    BANK_ID
)

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Hindsight AI Agent is running"
    }


@app.post("/chat")
def chat(user_message: str):

    result = ask_agent(user_message)

    return {
        "user_message": user_message,
        "answer": result["answer"],
        "used_memories": result["used_memories"]
    }


# 📌 NEW: Store Project Context
@app.post("/project-context")
def project_context(
    project_name: str,
    context: str
):

    remember_project_context(
        project_name=project_name,
        context=context
    )

    return {
        "message": "Project context saved successfully",
        "project_name": project_name,
        "context": context
    }


@app.get("/memories")
def memories():

    result = hindsight.recall(
        bank_id=BANK_ID,
        query="User preferences and important user information"
    )

    memories = []
    seen = set()

    for memory in result.results:

        text = memory.text.strip()
        lower_text = text.lower()

        if not any(word in lower_text for word in [
            "user preference",
            "user prefers",
            "user likes",
            "user favorite",
            "user doesn't like",
            "user does not like"
        ]):
            continue

        clean_text = text.replace(
            " | Involving: user",
            ""
        ).strip()

        if clean_text.lower() not in seen:

            seen.add(clean_text.lower())
            memories.append(clean_text)

    return {
        "memories": memories[:8]
    }


# 🧠 Memory Timeline
@app.get("/memory-timeline")
def memory_timeline():

    result = hindsight.recall(
        bank_id=BANK_ID,
        query="User preferences and important user information"
    )

    timeline = []
    seen = set()

    for memory in result.results:

        text = memory.text.strip()
        lower_text = text.lower()

        if not any(word in lower_text for word in [
            "user preference",
            "user prefers",
            "user likes",
            "user favorite",
            "user doesn't like",
            "user does not like"
        ]):
            continue

        clean_text = text.replace(
            " | Involving: user",
            ""
        ).strip()

        if clean_text.lower() in seen:
            continue

        seen.add(clean_text.lower())

        created_at = getattr(
            memory,
            "created_at",
            None
        )

        timeline.append({
            "memory": clean_text,
            "created_at": str(created_at)
            if created_at
            else "Previously remembered",
            "type": "User Preference"
        })

    return {
        "timeline": timeline[:10]
    }