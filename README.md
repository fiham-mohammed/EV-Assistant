# EV Assistant — v0.7

EV is a private personal AI assistant built in Python and powered by NVIDIA's hosted NIM API.

The project started as a simple command-line chatbot and has grown into a voice-enabled, memory-aware assistant with safe local file access and approved Windows PC tools.

## Current Version

**EV v0.7 — Intelligent PC Tools**

Current capabilities include:

- NVIDIA-powered AI conversation
- Persistent conversation memory
- Structured long-term memory
- Voice input
- Optional voice output
- Safe local file access
- Natural-language file understanding
- Current local time and date tools
- Approved application launching
- Safe calculator automation
- Notepad typing
- AI-generated Notepad writing
- Supported compound tool actions

---

## Requirements

- Windows
- Python 3.12 recommended
- NVIDIA API key
- Microphone for voice input
- Speakers/headphones for voice output

EV's current PC automation tools are designed for Windows.

---

## 1. Clone the Repository

```powershell
git clone https://github.com/fiham-mohammed/EV-Assistant.git
cd EV-Assistant
```

---

## 2. Create a Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 4. Configure NVIDIA NIM

Copy `.env.example` and rename the copy to `.env`.

Then add your NVIDIA API key:

```text
NVIDIA_API_KEY=nvapi-your-key-here
```

Optionally set the model:

```text
NVIDIA_MODEL=openai/gpt-oss-20b
```

Never commit your real `.env` file or API key to GitHub.

---

## 5. Run EV

```powershell
python ev.py
```

EV should start with a status screen similar to:

```text
EV v0.7
NVIDIA-powered personal AI assistant
Intelligent Memory: ONLINE
Voice Input: ONLINE
Voice Output: AVAILABLE
Safe File Access: ONLINE
Natural File Routing: ONLINE
Approved PC Tools: ONLINE
Safe Calculator: ONLINE
Intelligent Notepad: ONLINE
```

---

# Features

## AI Conversation

EV uses an NVIDIA-hosted language model through an OpenAI-compatible API.

Example:

```text
You: Explain machine learning simply.

EV: ...
```

---

## Persistent Conversation Memory

EV stores recent conversation history in SQLite so previous conversations can be restored after restarting the program.

Useful command:

```text
/clear-chat
```

This clears conversation history without deleting structured long-term memories.

---

## Structured Long-Term Memory

EV can store important facts separately from normal conversation history.

### Remember Something

```text
/remember identity name Fiham
```

```text
/remember project project_codename Orion
```

### View Memories

```text
/memories
```

### Forget One Memory

```text
/forget project project_codename
```

### Clear Everything

```text
/clear-all confirm
```

---

# Voice System

## Voice Input

Use:

```text
/voice
```

EV records microphone input and converts speech to text using Faster Whisper.

Example:

```text
You: /voice

[Voice] Listening...

You (voice): What is my project codename?

EV: ...
```

---

## Voice Output

Enable spoken responses:

```text
/speak-on
```

Disable spoken responses:

```text
/speak-off
```

When enabled, EV can speak AI answers and supported tool results.

---

# Safe File Access

EV does not have unrestricted access to the whole computer.

Local file access is restricted to EV's approved `data/` directory.

Supported file types currently include:

- `.txt`
- `.md`

## List Approved Files

```text
/files
```

## Read a File

```text
/read test.txt
```

With voice output enabled, EV can also read supported file contents aloud.

---

## Natural-Language File Understanding

EV can detect approved filenames in ordinary conversation and read the latest real file contents before answering.

Examples:

```text
What's inside test.txt?
```

```text
Summarize test.txt
```

```text
Explain test.txt
```

```text
How many lines does test.txt contain?
```

```text
What email address is in test.txt?
```

This prevents EV from relying only on old conversation history when answering questions about a file.

---

# Approved PC Tool System

EV v0.7 includes a controlled tool system.

The goal is to add useful computer actions without giving the AI unrestricted shell access.

## Current Time

```text
/time
```

or:

```text
EV, what time is it?
```

## Current Date

```text
/date
```

or:

```text
What's today's date?
```

## Open EV Data Folder

```text
/open-data
```

or:

```text
Open my data folder.
```

---

# Approved Applications

The current application allowlist contains:

- Notepad
- Calculator

Launch an approved application:

```text
/open notepad
```

```text
/open calculator
```

Natural language also works:

```text
Open Notepad.
```

```text
Open Calculator.
```

Applications outside the allowlist are rejected.

Example:

```text
/open chrome
```

EV should refuse unless Chrome is intentionally added to the allowlist.

---

# Safe Calculator

EV includes a restricted arithmetic calculator instead of using unrestricted Python evaluation.

Example:

```text
/calc 25*18
```

Natural language:

```text
What is 25 * 18?
```

EV can also open Windows Calculator and enter the calculation:

```text
Open Calculator and calculate 2+2
```

EV can process supported compound requests in one turn.

---

# Intelligent Notepad

EV can interact with approved Windows Notepad.

## Literal Typing

```text
Open Notepad and type hello world
```

EV opens Notepad and types exactly:

```text
hello world
```

## AI-Generated Writing

EV can also generate content with the NVIDIA model and place the generated answer into Notepad.

Examples:

```text
Open Notepad and explain what is AI
```

```text
Open Notepad and write about machine learning
```

```text
Open Notepad and describe artificial intelligence
```

Flow:

```text
User request
    ↓
EV detects Notepad writing intent
    ↓
NVIDIA generates the requested content
    ↓
EV opens approved Notepad
    ↓
EV types the generated response
```

EV currently does not automatically save the Notepad document.

---

# Commands

```text
exit                              Close EV

/voice                            Speak to EV
/speak-on                         Enable voice output
/speak-off                        Disable voice output

/files                            List approved files
/read <filename>                  Read an approved file

/time                             Show current local time
/date                             Show current local date
/calc <expression>                Calculate safely

/open-data                        Open EV data folder
/open <app>                       Launch approved app

/clear-chat                       Clear conversation history

/remember <category> <key> <value>
/memories
/forget <category> <key>

/clear-all confirm                Clear conversation and long-term memory
```

---

# Project Structure

A typical EV project directory looks like:

```text
EV-Assistant/
├── data/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── ev.py
├── file_tools.py
├── memory.py
├── pc_tools.py
├── speech.py
├── voice.py
└── requirements.txt
```

`data/` is EV's approved local-file area.

Keep private or personal files out of Git.

---

# Security Model

EV follows a controlled-tool approach.

Current safety rules include:

- No unrestricted shell execution
- No arbitrary PowerShell or terminal execution
- File access restricted to the approved `data/` folder
- Application launching restricted by an allowlist
- Safe arithmetic parsing instead of unrestricted `eval()`
- EV should only report an action as completed after the real tool succeeds
- File contents are treated as data, not trusted system instructions
- API keys remain in `.env`

The tool system should be expanded gradually rather than giving the assistant unrestricted computer control.

---

# Version History

## v0.1

- Initial NVIDIA NIM conversational assistant
- EV personality/system prompt

## v0.2

- Persistent conversation memory

## v0.3

- Structured long-term memory
- `/remember`
- `/memories`
- `/forget`

## v0.4

- Microphone input
- Faster Whisper speech-to-text

## v0.5

- Optional text-to-speech voice output

## v0.6

- Safe local file access
- Approved `data/` folder
- Natural-language file routing
- File questions and summarization

## v0.7

- Approved PC tool system
- Current time/date tools
- Approved application launching
- Safe calculator
- Windows Calculator automation
- Compound tool requests
- Notepad typing
- AI-generated Notepad writing

---

# Roadmap

## EV v0.8

Planned areas:

- Smarter task planning
- Better multi-step action execution
- Improved memory usage during actions
- Safe file creation and saving
- More natural tool selection
- Action history and clearer execution results

## Future Ideas

- PDF/document reading
- Larger-file search and chunking
- More approved desktop tools
- Vision and screen understanding
- Browser/web tools
- Scheduled automations
- Local/offline model support
- Personal knowledge base

---

# Author

**Fiham Mohammed**

EV Assistant is being developed step-by-step as a personal AI assistant with memory, voice, safe file access, and controlled computer tools.
