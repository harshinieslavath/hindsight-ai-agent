from agent import ask_agent

while True:
    user_message = input("\nYou: ")

    if user_message.lower() == "exit":
        break

    answer = ask_agent(user_message)

    print("\nAgent:", answer)