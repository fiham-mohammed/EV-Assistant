# EV v0.1

A minimal personal AI assistant using NVIDIA's hosted NIM API.

## 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

## 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 3. Add your NVIDIA API key

Copy `.env.example` and rename the copy to `.env`.

Then replace:

```text
NVIDIA_API_KEY=nvapi-your-key-here
```

with your real NVIDIA API key.

Never upload `.env` to GitHub.

## 4. Run EV

```bash
python ev.py
```

Try:

```text
Hello EV. Introduce yourself.
```

Then have a short conversation to confirm context is retained during the current session.

## Current abilities

- Text chat
- Conversation context during one session
- EV personality/system prompt
- NVIDIA-hosted AI model

## Next versions

- v0.2 persistent memory
- v0.3 voice
- v0.4 tools and computer actions
- v0.5 file/RAG knowledge
- v0.6 vision
