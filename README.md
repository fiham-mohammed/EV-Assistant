# EV Assistant — v0.9.0

EV is a private personal AI assistant built in Python and powered by NVIDIA's hosted NIM API.

EV has grown from a simple command-line chatbot into a memory-aware, voice-enabled assistant with safe file access, controlled Windows tools, structured planning, validated execution, persistent task history, and a central tool registry.

---

# Current Version

## EV v0.9.0 — Modular Tool Registry, Task History & Safe File Writing

EV v0.9 introduces a central tool registry and expands EV's safe local automation capabilities.

Current capabilities include:

- NVIDIA-powered AI conversation
- Persistent conversation memory
- Structured long-term memory
- Voice input
- Optional voice output
- Safe local file access
- Natural-language file understanding
- Safe creation of new `.txt` and `.md` files
- Safe append-only updates to existing `.txt` and `.md` files
- Current local time and date tools
- Approved application launching
- Safe arithmetic calculator
- Windows Calculator automation
- Literal Notepad typing
- AI-generated Notepad writing
- Safe task-plan preview
- Validated task execution
- Central tool registry
- Registry-backed planner validation
- Registry-backed executor dispatch
- Persistent task execution history
- Strict filename/path validation
- Unsupported-action rejection
- Safe literal/generated-text routing

---

# Requirements

- Windows
- Python 3.12 recommended
- NVIDIA API key
- Microphone for voice input
- Speakers/headphones for voice output

EV's current PC automation tools are designed primarily for Windows.

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

A typical EV v0.9 startup screen includes:

```text
EV v0.9
NVIDIA-powered personal AI assistant
Intelligent Memory: ONLINE
Voice Input: ONLINE
Voice Output: AVAILABLE
Safe File Access: ONLINE
Natural File Routing: ONLINE
Safe File Creation: ONLINE
Safe File Append: ONLINE
Approved PC Tools: ONLINE
Safe Calculator: ONLINE
Intelligent Notepad: ONLINE
Safe Task Planner: PREVIEW ONLY
Safe Plan Executor: ONLINE
Central Tool Registry: ONLINE
Registered Planner Actions: 9
Persistent Task History: ONLINE
```

---

# AI Conversation

EV uses an NVIDIA-hosted language model through an OpenAI-compatible API.

Example:

```text
You: Explain machine learning simply.
EV: ...
```

---

# Persistent Conversation Memory

EV stores recent conversation history in SQLite so conversations can be restored after restarting the application.

Clear conversation history:

```text
/clear-chat
```

This does not remove structured long-term memory or task history.

---

# Structured Long-Term Memory

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

Clear conversation and long-term memory:

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

## Voice Output

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

EV does not have unrestricted filesystem access.

File access is restricted to EV's approved `data/` directory.

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

Current real file-tool results override older conversation claims about that file.

File contents are treated as untrusted data, not trusted system instructions.

---

# Safe File Creation

EV v0.9 can create new `.txt` and `.md` files inside the approved `data/` directory.

Literal content example:

```text
/run-plan Create notes.txt with hello
```

Expected plan:

```text
1. create_file -> {'filename': 'notes.txt', 'text': 'hello'}
```

Generated content example:

```text
/run-plan Create ai_notes.txt with a short explanation of AI
```

Expected plan:

```text
1. generate_text -> {'prompt': 'Create a short explanation of AI'}
2. create_file -> {'filename': 'ai_notes.txt', 'source': 'generated_text'}
```

Safety rules:

- only `.txt` and `.md`
- only inside `data/`
- no absolute paths
- no nested directory paths
- no `../` traversal
- no drive prefixes
- existing files are not overwritten

If a file already exists, `create_file` refuses the operation.

---

# Safe File Append

EV v0.9 can append text to an existing approved `.txt` or `.md` file.

Literal append:

```text
/run-plan Append goodbye to notes.txt
```

Expected plan:

```text
1. append_file -> {'filename': 'notes.txt', 'text': 'goodbye'}
```

Generated append:

```text
/run-plan Append a short AI tip to notes.txt
```

Expected plan:

```text
1. generate_text -> {'prompt': 'Create a short practical AI tip'}
2. append_file -> {'filename': 'notes.txt', 'source': 'generated_text'}
```

Append safety:

- target file must already exist
- existing content is preserved
- append never truncates the file
- approved extensions only
- approved `data/` directory only
- unsafe paths are rejected
- missing files are refused

---

# Approved PC Tool System

EV uses a controlled tool architecture.

Current approved PC capabilities include:

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

The calculator applies operator, exponent, and result limits.

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

# Central Tool Registry

EV v0.9 introduces `tool_registry.py` as the source of truth for planner and executor policy.

The registry defines:

- approved action names
- approved application names
- argument schemas
- approved filename extensions
- argument length limits
- action normalization
- filename validation
- generated-text dependency rules
- redundant-step cleanup
- planner action references

This reduces duplicated policy logic across `planner.py` and `executor.py`.

---

# Registered Planner Actions

EV v0.9 currently has 9 registered actions:

```text
append_file
calculate
create_file
generate_text
get_date
get_time
open_app
open_data_folder
write_notepad
```

## `get_time`

```text
args: {}
```

Gets the real current local time.

## `get_date`

```text
args: {}
```

Gets the real current local date.

## `calculate`

```text
args: {'expression': '25*18'}
```

Safely evaluates an approved arithmetic expression.

## `open_app`

```text
args: {'app': 'notepad'}
```

Launches an application from EV's approved application allowlist.

## `open_data_folder`

```text
args: {}
```

Opens EV's approved `data/` folder.

## `generate_text`

```text
args: {'prompt': 'Create a short explanation of AI'}
```

Generates plain text for an approved task.

## `write_notepad`

Literal:

```text
args: {'text': 'hello'}
```

Generated:

```text
args: {'source': 'generated_text'}
```

## `create_file`

Literal:

```text
args: {'filename': 'notes.txt', 'text': 'hello'}
```

Generated:

```text
args: {'filename': 'notes.txt', 'source': 'generated_text'}
```

## `append_file`

Literal:

```text
args: {'filename': 'notes.txt', 'text': 'goodbye'}
```

Generated:

```text
args: {'filename': 'notes.txt', 'source': 'generated_text'}
```

---

# Safe Task Planner

Preview a task plan:

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

`/plan` is preview-only and does not execute actions.

---

# Safe Plan Executor

Execute a validated task:

```text
/run-plan <task>
```

Execution flow:

```text
User request
    ↓
NVIDIA planner
    ↓
JSON parser
    ↓
Central tool registry
    ↓
Action validation
    ↓
Argument-schema validation
    ↓
Dependency validation
    ↓
Executor handler dispatch
    ↓
Approved Python tool function
```

Example:

```text
/run-plan Open Notepad and create a short AI study plan
```

Possible output:

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

# Registry-Backed Executor

EV v0.9 uses an explicit `ACTION_HANDLERS` dispatch table.

The executor checks that:

- every registered action has a handler
- no executor handler exists for an unregistered action
- unknown actions cannot execute
- every plan is validated before execution
- handler results are checked before reporting success

No dynamic shell, `eval`, or `exec` dispatch is used.

---

# Persistent Task History

EV v0.9 stores planner/executor history in SQLite.

Task history records compact metadata only:

- request
- goal
- status
- action names
- error text when relevant
- timestamp

It does not store generated Notepad/file content in the task-history entry.

Show recent history:

```text
/history
```

Show a limited number of entries:

```text
/history 5
```

Clear task history:

```text
/history-clear confirm
```

Possible statuses:

```text
PREVIEWED
EXECUTED
REFUSED
FAILED
```

Task history persists across EV restarts.

---

# Filename Binding Protection

A language model may sometimes try to rewrite an unsafe path into a safe-looking filename.

Example request:

```text
Create ../escape.txt with hello
```

A model might try to change that into:

```text
escape.txt
```

EV v0.9 binds explicit filenames from the original user request to the validated plan so unsafe path syntax cannot be silently removed.

Unsafe filenames are validated exactly as requested.

Examples that should be rejected by file-writing policy:

```text
../escape.txt
C:\temp\notes.txt
folder/notes.txt
script.py
```

---

# Literal vs Generated Content Routing

EV distinguishes literal text from AI-generated content.

Literal request:

```text
Create notes.txt with hello
```

Plan:

```text
1. create_file -> {'filename': 'notes.txt', 'text': 'hello'}
```

No unnecessary `generate_text` step is executed.

Generated request:

```text
Create notes.txt with a short explanation of AI
```

Plan:

```text
1. generate_text -> {'prompt': 'Create a short explanation of AI'}
2. create_file -> {'filename': 'notes.txt', 'source': 'generated_text'}
```

The same cleanup applies to Notepad and append workflows.

---

# Planner Preview Guard

Planner/debug output is display text only.

For example:

```text
open_app -> {"app": "notepad"}
```

is not treated as an executable command.

The preview guard reads approved action names from the central tool registry instead of using a hardcoded action list.

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

/history [limit]                  Show persistent task history
/history-clear confirm            Clear task history

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
├── file_write_tools.py
├── memory.py
├── pc_tools.py
├── planner.py
├── speech.py
├── task_history.py
├── tool_registry.py
├── voice.py
└── requirements.txt
```

## `ev.py`

Main application loop, command routing, conversation handling, memory context, file context, planner/executor integration, history commands, and startup UI.

## `tool_registry.py`

Central source of truth for approved actions, schemas, app policy, filename rules, dependencies, and normalization.

## `planner.py`

Creates structured plans, parses model JSON, validates the plan envelope, binds explicit filenames to the original request, and delegates tool validation to the registry.

## `executor.py`

Executes only validated approved actions through an explicit handler dispatch table.

## `task_history.py`

Stores persistent planner/executor history inside EV's SQLite database.

## `file_tools.py`

Restricts file reading to the approved EV `data/` folder.

## `file_write_tools.py`

Handles safe creation and append-only updates for approved `.txt` and `.md` files.

## `pc_tools.py`

Contains approved Windows PC tools such as current time/date, approved app launching, safe calculator, Calculator UI interaction, and Notepad typing.

## `memory.py`

SQLite-backed conversation and structured long-term memory.

## `voice.py`

Microphone recording and Faster Whisper speech-to-text.

## `speech.py`

Optional text-to-speech output.

---

# Security Model

EV follows a controlled-tool approach.

Current rules include:

- No unrestricted shell execution
- No arbitrary PowerShell execution
- No arbitrary Command Prompt execution
- No arbitrary `eval()` or `exec()`
- File reading restricted to the approved `data/` folder
- File writing restricted to the approved `data/` folder
- Safe file creation supports only `.txt` and `.md`
- New-file creation refuses existing-file overwrite
- Append only works on existing approved files
- Unsafe paths and traversal attempts are rejected
- Explicit user filenames are bound to validated plans
- Application launching restricted by an allowlist
- Safe AST arithmetic instead of unrestricted `eval()`
- Planner actions restricted by the central tool registry
- Planner arguments validated before execution
- Generated-text dependencies are validated
- Executor handler alignment is checked
- Unsupported plans execute nothing
- Planner preview text is never treated as a tool call
- File contents are treated as untrusted data
- API keys stay in `.env`
- EV should only report successful tool actions after the real tool succeeds

The tool system should continue to expand gradually instead of giving the AI unrestricted computer control.

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
- Multi-step Notepad execution
- Planner preview syntax guard
- Improved Notepad typing reliability

## v0.9

- Central `tool_registry.py`
- Registry-backed planner validation
- Registry-backed executor dispatch
- 9 registered planner actions
- Persistent task execution history
- `/history`
- `/history-clear confirm`
- Safe `.txt` and `.md` file creation
- Safe append-only file updates
- Existing-file overwrite protection
- Missing append-target rejection
- Filename/path validation
- Explicit request-to-plan filename binding
- Path traversal rejection
- Literal/generated content routing cleanup
- Improved planner normalization

---

# Roadmap

## EV v0.10

Possible next areas:

- Refactor the large `ev.py` main loop into smaller command/router modules
- Add automated tests for planner/registry/executor behavior
- Improve tool metadata and capability introspection
- Add task-history filtering
- Improve execution reports
- Improve multi-step data flow between tools
- Better planner use of structured long-term memory
- Consider safe file replacement only with explicit confirmation
- Consider safe file deletion only with explicit confirmation

## Future Ideas

- PDF/document reading
- Larger-file chunking and search
- Additional approved desktop tools
- Vision and screen understanding
- Browser/web tools
- Scheduled automations
- Local/offline AI model support
- Personal knowledge base
- Smart-device integrations

---

# Author

**Fiham Mohammed**

EV Assistant is being developed step-by-step from a simple AI chatbot into a memory-aware, voice-enabled, tool-using personal assistant with controlled and validated computer actions.
