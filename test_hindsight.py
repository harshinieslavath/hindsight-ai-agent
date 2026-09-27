import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

BANK_ID = "hackathon-agent"

client.retain(
    bank_id=BANK_ID,
    content="The user prefers Python for backend development."
)

result = client.recall(
    bank_id=BANK_ID,
    query="What does the user prefer for backend development?"
)

print("MEMORIES FOUND:")

for memory in result.results:
    print("-", memory.text)

client.close()