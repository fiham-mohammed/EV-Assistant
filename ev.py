import os

from dotenv import load_dotenv
from openai import OpenAI

from memory import (
    initialize_memory,
    save_message,
    load_recent_messages,
    clear_memory,
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
print("EV v0.2")
print("NVIDIA-powered personal AI assistant")
print("Persistent Memory: ONLINE")
print()
print("Commands:")
print("  exit      Close EV")
print("  /clear    Clear conversation memory")
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
        # Clear persistent memory
        # ------------------------------

        if user_input.lower() == "/clear":
            clear_memory()

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            print("\nEV: My conversation memory has been cleared.")
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
        # Send request to NVIDIA
        # ------------------------------

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
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