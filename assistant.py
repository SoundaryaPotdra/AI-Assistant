from gpt_brain import (
    interpret_with_gpt,
    generate_chat_summary
)

from utils.voice_io import listen, speak
from command_router import route_command

from memory_manager import save_chat_summary


def run_assistant():

    speak("Hello! I am your personal assistant.")

    # Current session only (TEMPORARY MEMORY)
    conversation_history = []

    while True:

        command = listen()

        if not command:
            continue

        if "exit" in command.lower() or "stop" in command.lower():

            speak("Goodbye!")

            if conversation_history:

                try:

                    summary = generate_chat_summary(
                        conversation_history
                    )

                    if summary:
                        save_chat_summary(summary)

                except Exception as e:

                    print(
                        "Summary error:",
                        e
                    )

            break

        # SAVE USER MESSAGE TO TEMP MEMORY
        conversation_history.append({
            "role": "user",
            "content": command
        })

        # GPT
        gpt_response = interpret_with_gpt(
            command,
            conversation_history[:-1]
        )

        print("GPT:", gpt_response)

        # SAVE GPT COMMAND TO TEMP MEMOR
        conversation_history.append({
            "role": "assistant",
            "content": gpt_response
        })

        # EXECUT
        route_command(gpt_response)


if __name__ == "__main__":
    run_assistant()