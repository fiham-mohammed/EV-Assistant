import os

from dotenv import load_dotenv
from openai import OpenAI

from memory import (
    initialize_memory,
    save_message,
    load_recent_messages,
    clear_conversation_memory,
    save_memory,
    load_all_memories,
    delete_memory,
    clear_long_term_memory,
    clear_all_memory,
)


load_dotenv(override=True)

API_KEY = os.getenv("NVIDIA_API_KEY")
MODEL = os.getenv("NVIDIA_MODEL", "openai/gpt-oss-20b")

if not API_KEY:
    raise RuntimeError(
        "NVIDIA_API_KEY was not found. Copy .env.example to .env "
        "and put your NVIDIA API key there."
    )


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=API_KEY,
)


SYSTEM_PROMPT = """
You are EV, a private personal AI assistant.

Personality:
- calm, intelligent, concise, friendly
- proactive without being annoying
- explain technical topics simply
- never pretend an action was completed unless a tool actually completed it

You may receive previous conversations stored in persistent memory.
Use those previous conversations when they are relevant.

Current capabilities:
- conversation
- persistent conversation memory

Future versions will receive voice, computer tools, vision, and automation.
""".strip()


# ==========================================
# Initialize persistent memory
# ==========================================

initialize_memory()

previous_messages = load_recent_messages(limit=30)


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

messages.extend(previous_messages)


print("=" * 55)
print("EV v0.3")
print("NVIDIA-powered personal AI assistant")
print("Persistent Memory: ONLINE")
print()
print("Commands:")
print("  exit                              Close EV")
print("  /clear-chat                       Clear chat history")
print("  /remember <category> <key> <value>")
print("  /memories                         Show long-term memories")
print("  /forget <category> <key>")
print("  /clear-all confirm                Clear everything")
print("=" * 55)


while True:
    try:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        # ------------------------------
        # Exit EV
        # ------------------------------

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("\nEV: Goodbye.")
            break

        # ------------------------------
        # Clear conversation history
        # ------------------------------

        if user_input.lower() in {"/clear", "/clear-chat"}:
            clear_conversation_memory()

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            print("\nEV: Conversation history cleared.")
            continue


        # ------------------------------
        # Show long-term memories
        # ------------------------------

        if user_input.lower() == "/memories":
            memories = load_all_memories()

            if not memories:
                print("\nEV: I don't have any long-term memories yet.")
            else:
                print("\nEV Long-Term Memories")
                print("-" * 40)

                for memory in memories:
                    print(
                        f"[{memory['category']}] "
                        f"{memory['key']} = {memory['value']}"
                    )

            continue


        # ------------------------------
        # Save long-term memory
        # Example:
        # /remember project project_codename Orion
        # ------------------------------

        if user_input.lower().startswith("/remember "):
            parts = user_input.split(maxsplit=3)

            if len(parts) != 4:
                print(
                    "\nEV: Use:\n"
                    "/remember <category> <key> <value>"
                )
                continue

            _, category, memory_key, memory_value = parts

            save_memory(
                category,
                memory_key,
                memory_value
            )

            print(
                f"\nEV: Remembered "
                f"[{category}] {memory_key} = {memory_value}"
            )

            continue


        # ------------------------------
        # Forget one long-term memory
        # Example:
        # /forget project project_codename
        # ------------------------------

        if user_input.lower().startswith("/forget "):
            parts = user_input.split(maxsplit=2)

            if len(parts) != 3:
                print(
                    "\nEV: Use:\n"
                    "/forget <category> <key>"
                )
                continue

            _, category, memory_key = parts

            delete_memory(
                category,
                memory_key
            )

            print(
                f"\nEV: Removed memory "
                f"[{category}] {memory_key}"
            )

            continue


        # ------------------------------
        # Clear ALL memory
        # ------------------------------

        if user_input.lower() == "/clear-all confirm":
            clear_all_memory()

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            print(
                "\nEV: Conversation history and "
                "long-term memory cleared."
            )

            continue

        # ------------------------------
        # Add user message
        # ------------------------------

        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        # Save user message permanently
        save_message(
            "user",
            user_input
        )

        # ------------------------------
        # Load long-term memory
        # ------------------------------

        long_term_memories = load_all_memories()

        memory_lines = []

        for memory in long_term_memories:
            memory_lines.append(
                f"- [{memory['category']}] "
                f"{memory['key']} = {memory['value']}"
            )


        if memory_lines:
            memory_context = (
                "The following are confirmed long-term memories "
                "about the user:\n"
                + "\n".join(memory_lines)
                + "\n\nUse these memories only when relevant."
            )
        else:
            memory_context = (
                "There are currently no saved long-term memories."
            )


        request_messages = [
            messages[0],
            {
                "role": "system",
                "content": memory_context
            },
            *messages[1:]
        ]

        # ------------------------------
        # Send request to NVIDIA
        # ------------------------------

        response = client.chat.completions.create(
            model=MODEL,
            messages=request_messages,
            temperature=0.6,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content or ""

        # ------------------------------
        # Add EV response
        # ------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        # Save EV response permanently
        save_message(
            "assistant",
            answer
        )

        print(f"\nEV: {answer}")

    except KeyboardInterrupt:
        print("\n\nEV: Goodbye.")
        break

    except Exception as exc:
        print(f"\n[ERROR] {exc}")