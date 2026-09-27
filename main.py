from fastapi import FastAPI
from agent import ask_agent, hindsight, BANK_ID

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Hindsight AI Agent is running"
    }


@app.post("/chat")
def chat(user_message: str):
    answer = ask_agent(user_message)

    return {
        "user_message": user_message,
        "answer": answer
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

        # Only show useful user-related memories
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

        # Remove duplicate memories
        clean_text = text.replace(" | Involving: user", "").strip()

        if clean_text.lower() not in seen:
            seen.add(clean_text.lower())
            memories.append(clean_text)

    return {
        "memories": memories[:8]
    }