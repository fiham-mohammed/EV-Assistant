# EV Assistant — v0.8.0

EV is a private personal AI assistant built in Python and powered by NVIDIA's hosted NIM API.

The project started as a simple command-line chatbot and has grown into a memory-aware, voice-enabled assistant with safe local file access, controlled Windows PC tools, intelligent Notepad writing, and a validated multi-step task planning system.

---

# Current Version

## EV v0.8.0 — Safe Task Planner & Validated Executor

EV v0.8 introduces a structured planning layer between natural-language requests and computer actions.

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
- Safe arithmetic calculator
- Windows Calculator automation
- Literal Notepad typing
- AI-generated Notepad writing
- Safe task-plan preview
- Validated task execution
- Supported multi-step actions
- Strict planner action allowlist
- Planner argument validation
- Unsupported-action rejection

---

# Requirements

- Windows
- Python 3.12 recommended
- NVIDIA API key
- Microphone for voice input
- Speakers/headphones for voice output

EV's current PC automation tools are designed for Windows.

---

# Installation

## 1. Clone the Repository

```powershell
git clone https://github.com/fiham-mohammed/EV-Assistant.git
cd EV-Assistant
```

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

## 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

## 4. Configure NVIDIA NIM

Copy `.env.example` and rename the copy to `.env`.

Add your NVIDIA API key:

```text
NVIDIA_API_KEY=nvapi-your-key-here
```

Optionally set the model:

```text
NVIDIA_MODEL=openai/gpt-oss-20b
```

Never commit your real `.env` file or API key to GitHub.

## 5. Run EV

```powershell
python ev.py
```

A typical EV v0.8 startup screen includes:

```text
EV v0.8
NVIDIA-powered personal AI assistant
Intelligent Memory: ONLINE
Voice Input: ONLINE
Voice Output: AVAILABLE
Safe File Access: ONLINE
Natural File Routing: ONLINE
Approved PC Tools: ONLINE
Safe Calculator: ONLINE
Intelligent Notepad: ONLINE
Safe Task Planner: PREVIEW ONLY
Safe Plan Executor: ONLINE
```

---

# Features

## AI Conversation

EV uses an NVIDIA-hosted language model through an OpenAI-compatible API.

## Persistent Memory

EV stores recent conversation history in SQLite so previous conversations can be restored after restarting the application.

Clear conversation history:

```text
/clear-chat
```

## Structured Long-Term Memory

Remember something:

```text
/remember identity name Fiham
```

View memories:

```text
/memories
```

Forget one memory:

```text
/forget identity name
```

Clear everything:

```text
/clear-all confirm
```

---

# Voice System

Voice input:

```text
/voice
```

Enable spoken responses:

```text
/speak-on
```

Disable spoken responses:

```text
/speak-off
```

---

# Safe File Access

EV does not have unrestricted access to the computer's filesystem.

Local file access is restricted to EV's approved `data/` directory.

Current supported file types:

- `.txt`
- `.md`

List approved files:

```text
/files
```

Read a file:

```text
/read test.txt
```

Natural-language examples:

```text
What's inside test.txt?
Summarize test.txt
Explain test.txt
How many lines does test.txt contain?
```

Current file-tool results override older conversation claims about that file.

File contents are treated as data, not trusted system instructions.

---

# Approved PC Tool System

EV uses a controlled tool architecture.

Current approved tools include:

- Current local time
- Current local date
- EV data-folder access
- Notepad
- Calculator
- Safe arithmetic evaluation
- Controlled Notepad typing

Time:

```text
/time
```

Date:

```text
/date
```

Open the approved data folder:

```text
/open-data
```

Launch approved apps:

```text
/open notepad
/open calculator
```

Applications outside the allowlist are rejected.

---

# Safe Calculator

EV uses a restricted AST-based arithmetic evaluator instead of unrestricted `eval()`.

Examples:

```text
/calc 25*18
```

```text
Open Calculator and calculate 2+2
```

---

# Intelligent Notepad

Literal typing:

```text
Open Notepad and type hello world
```

AI-generated writing:

```text
Open Notepad and explain what is AI
```

```text
Open Notepad and write about machine learning
```

EV currently does not automatically save the Notepad document.

---

# EV v0.8 Safe Task Planner

Preview a plan:

```text
/plan <task>
```

Example:

```text
/plan Open Notepad and create a short AI study plan
```

Example output:

```text
EV Plan
----------------------------------------
Goal: Create a short AI study plan in Notepad
1. generate_text -> {'prompt': 'Create a short practical AI study plan'}
2. write_notepad -> {'source': 'generated_text'}
```

`/plan` is preview-only and does not execute the actions.

---

# Safe Plan Executor

Execute a validated plan:

```text
/run-plan <task>
```

Example:

```text
/run-plan Open Notepad and create a short AI study plan
```

Execution flow:

```text
User request
    ↓
NVIDIA planner
    ↓
JSON parser
    ↓
Action allowlist validation
    ↓
Argument-schema validation
    ↓
Dependency validation
    ↓
Safe executor
    ↓
Approved Python tool functions
```

Example execution:

```text
EV Plan
----------------------------------------
Goal: Create a short AI study plan in Notepad
1. generate_text -> {'prompt': 'Create a short practical AI study plan'}
2. write_notepad -> {'source': 'generated_text'}

EV Execution
----------------------------------------
1. generate_text: Generated the requested text.
2. write_notepad: Opened Notepad and typed the requested text.
```

---

# Planner Safety

Current allowed planner actions:

```text
get_time
get_date
calculate
open_app
open_data_folder
write_notepad
generate_text
```

Unsupported requests produce an empty plan.

Example:

```text
/run-plan Run a PowerShell command
```

Expected behavior:

```text
Goal: Unsupported request
No approved actions available for this request.
```

Planner/debug output is display text only.

For example:

```text
open_app -> {"app": "notepad"}
```

is not treated as an executable command.

---

# Available Commands

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

/plan <task>                      Preview a safe task plan
/run-plan <task>                  Execute a validated safe task plan

/clear-chat                       Clear conversation history

/remember <category> <key> <value>
/memories
/forget <category> <key>

/clear-all confirm                Clear conversation and long-term memory
```

---

# Project Structure

```text
EV-Assistant/
├── data/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── ev.py
├── executor.py
├── file_tools.py
├── memory.py
├── pc_tools.py
├── planner.py
├── speech.py
├── voice.py
└── requirements.txt
```

## Main Modules

### `ev.py`
Main application loop, command routing, conversation handling, memory context, file context, and tool integration.

### `planner.py`
Creates and validates structured safe task plans.

### `executor.py`
Executes only validated approved planner actions.

### `pc_tools.py`
Contains approved Windows PC tools such as current time/date, approved app launching, safe calculator, Calculator UI interaction, and Notepad typing.

### `file_tools.py`
Restricts local file access to the approved EV `data/` folder.

### `memory.py`
SQLite-backed conversation and structured long-term memory.

### `voice.py`
Microphone recording and Faster Whisper speech-to-text.

### `speech.py`
Optional text-to-speech output.

---

# Security Model

EV follows a controlled-tool approach.

Current rules include:

- No unrestricted shell execution
- No arbitrary PowerShell execution
- No arbitrary Command Prompt execution
- File access restricted to the approved `data/` folder
- Application launching restricted by an allowlist
- Safe AST arithmetic instead of unrestricted `eval()`
- Planner actions restricted by an allowlist
- Planner arguments validated before execution
- Executor validates plans again before running actions
- Unsupported plans execute nothing
- Planner preview text is never treated as an executable tool call
- EV should only report successful tool actions after the real tool succeeds
- File contents are treated as untrusted data
- API keys stay in `.env`

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

## v0.8
- Structured safe task planner
- `/plan` preview command
- Validated safe plan executor
- `/run-plan` execution command
- Strict planner action allowlist
- Strict planner argument schemas
- Unsupported-action rejection
- Generated-text task pipeline
- Multi-step Notepad task execution
- Planner preview syntax guard
- Improved Notepad typing reliability

---

# Roadmap

## EV v0.9

Possible next areas:

- Persistent task/action history
- Better planner consistency
- More reusable multi-step actions
- Safe file creation
- Safe file writing and saving
- Better planner use of structured memory
- More detailed execution reports
- Modular tool registry
- Refactoring the large `ev.py` application loop

## Future Ideas

- PDF/document reading
- Larger-file chunking and search
- Additional approved desktop tools
- Vision and screen understanding
- Browser/web tools
- Scheduled automations
- Local/offline AI model support
- Personal knowledge base

---

# Author

**Fiham Mohammed**

EV Assistant is being developed step-by-step from a simple AI chatbot into a memory-aware, voice-enabled, tool-using personal assistant with controlled and validated computer actions.
