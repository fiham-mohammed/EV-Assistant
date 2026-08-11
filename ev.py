import os
from dotenv import load_dotenv
from openai import OpenAI

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

For this first version, you can only have conversations.
Future versions will receive memory, voice, computer tools, vision, and automation.
""".strip()

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

print("=" * 52)
print("EV v0.1")
print("NVIDIA-powered personal AI assistant")
print("Type 'exit' to close EV.")
print("=" * 52)

while True:
    try:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("\nEV: Goodbye.")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.6,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": answer})

        print(f"\nEV: {answer}")

    except KeyboardInterrupt:
        print("\n\nEV: Goodbye.")
        break
    except Exception as exc:
        print(f"\n[ERROR] {exc}")
