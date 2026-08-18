import json
import re

from tool_registry import (
    MAX_PLAN_STEPS,
    build_planner_action_reference,
    get_allowed_actions,
    normalize_plan_steps,
    validate_tool_args,
)


# =====================================================
# EV v0.9 Safe Task Planner
# =====================================================

MAX_GOAL_CHARS = 300


# =====================================================
# Planner Prompt
# =====================================================

PLANNER_SYSTEM_PROMPT = f"""
You are EV's safe task planner.

Your job is to convert a user's request into a short JSON plan.

You DO NOT execute actions.

{build_planner_action_reference()}

Important planning rules:

- Return JSON only.
- Never return Markdown.
- Never wrap JSON in code fences.
- Never invent an action.
- Never use shell commands.
- Never use PowerShell.
- Never use Command Prompt.
- Never run terminal commands.
- Never execute code.
- Never claim that an action already happened.
- Only use applications approved by EV's tool registry.
- Keep plans short.
- Use lowercase action names.
- Use the exact argument names defined by the tool registry.
- If the user's request cannot be completed using ONLY approved actions,
  return an empty steps list.
- Do not explain rejected requests outside the JSON.

File append rules:

- append_file appends to an EXISTING approved .txt or .md file.
- append_file never truncates or overwrites the existing file.
- Only simple filenames inside EV's approved data folder are allowed.
- If the user provides literal text to append, use append_file with
  "filename" and "text" and do NOT add generate_text.
- If the user asks EV to generate new content to append, first use
  generate_text, then append_file with "filename" and
  {{"source": "generated_text"}}.
- Preserve any filename explicitly written by the user exactly.

File creation rules:

- create_file creates NEW files only inside EV's approved data folder.
- Only .txt and .md filenames are approved.
- Never use an absolute path or directory path.
- Never overwrite an existing file.
- If the user provides literal content, use create_file with "filename" and "text".
- If create_file uses literal "text", do NOT add a generate_text step.
- If the user asks EV to generate content for a file, first use generate_text,
  then create_file with "filename" and {{"source": "generated_text"}}.
- Never use {{"text": "generated_text"}} as a placeholder.
- When consuming generated content, always use {{"source": "generated_text"}}.
- Do not invent unsupported file extensions.
- Preserve any filename explicitly written by the user exactly.
- Never remove ../, directory separators, drive prefixes, or other path syntax
  to make an unsafe filename appear safe.
- If an explicit requested filename is unsafe, let validation reject it.

Notepad rules:

- write_notepad already opens/focuses approved Notepad.
- Do NOT add open_app for Notepad when the plan also uses write_notepad.
- If the user asks to type literal text, use write_notepad with "text".
- If write_notepad uses literal "text", do NOT add a generate_text step.
- If the user asks EV to create, explain, describe, prepare, draft, or write
  new content in Notepad, first use generate_text and then use write_notepad
  with {{"source": "generated_text"}}.
- Never put placeholder phrases such as "generated text",
  "AI study plan text", or "content goes here" in write_notepad.
- If generate_text is used for Notepad, write_notepad must reference
  "generated_text".

Return exactly this general structure:

{{
  "goal": "short description of the user's goal",
  "steps": [
    {{
      "action": "approved_action_name",
      "args": {{}}
    }}
  ]
}}

Example: get time

User:
What time is it?

Response:
{{
  "goal": "Get the current local time",
  "steps": [
    {{
      "action": "get_time",
      "args": {{}}
    }}
  ]
}}

Example: literal Notepad typing

User:
Open Notepad and type hello world

Response:
{{
  "goal": "Type hello world in Notepad",
  "steps": [
    {{
      "action": "write_notepad",
      "args": {{
        "text": "hello world"
      }}
    }}
  ]
}}

Example: AI-generated Notepad writing

User:
Open Notepad and create a short AI study plan

Response:
{{
  "goal": "Create a short AI study plan in Notepad",
  "steps": [
    {{
      "action": "generate_text",
      "args": {{
        "prompt": "Create a short practical AI study plan"
      }}
    }},
    {{
      "action": "write_notepad",
      "args": {{
        "source": "generated_text"
      }}
    }}
  ]
}}

Example: AI-generated file creation

User:
Create study_plan.txt with a short AI study plan

Response:
{{
  "goal": "Create a short AI study plan file",
  "steps": [
    {{
      "action": "generate_text",
      "args": {{
        "prompt": "Create a short practical AI study plan"
      }}
    }},
    {{
      "action": "create_file",
      "args": {{
        "filename": "study_plan.txt",
        "source": "generated_text"
      }}
    }}
  ]
}}

Example: append literal text

User:
Append hello to notes.txt

Response:
{{
  "goal": "Append hello to notes.txt",
  "steps": [
    {{
      "action": "append_file",
      "args": {{
        "filename": "notes.txt",
        "text": "hello"
      }}
    }}
  ]
}}

Example: append generated text

User:
Append a short AI tip to notes.txt

Response:
{{
  "goal": "Append a short AI tip to notes.txt",
  "steps": [
    {{
      "action": "generate_text",
      "args": {{
        "prompt": "Create a short practical AI tip"
      }}
    }},
    {{
      "action": "append_file",
      "args": {{
        "filename": "notes.txt",
        "source": "generated_text"
      }}
    }}
  ]
}}

Example: unsupported request

User:
Run a PowerShell command

Response:
{{
  "goal": "Unsupported request",
  "steps": []
}}
""".strip()


# =====================================================
# Planner Validation
# =====================================================

def _require_goal(value):
    if not isinstance(
        value,
        str,
    ):
        raise ValueError(
            "Planner field 'goal' must be a string."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            "Planner field 'goal' cannot be empty."
        )

    if len(value) > MAX_GOAL_CHARS:
        raise ValueError(
            "Planner field 'goal' is too long."
        )

    return value


def validate_plan(plan):
    """
    Validate the planner envelope here, then delegate all
    tool/step validation to EV's central tool registry.
    """

    if not isinstance(
        plan,
        dict,
    ):
        raise ValueError(
            "Planner response must be a JSON object."
        )

    allowed_top_level_keys = {
        "goal",
        "steps",
    }

    if set(plan.keys()) != allowed_top_level_keys:
        raise ValueError(
            "Planner response must contain only "
            "'goal' and 'steps'."
        )

    goal = _require_goal(
        plan[
            "goal"
        ]
    )

    steps = plan[
        "steps"
    ]

    if not isinstance(
        steps,
        list,
    ):
        raise ValueError(
            "Planner response must contain "
            "a steps list."
        )

    if len(steps) > MAX_PLAN_STEPS:
        raise ValueError(
            "Planner returned too many steps."
        )

    normalized_steps = normalize_plan_steps(
        steps
    )

    return {
        "goal": goal,
        "steps": normalized_steps,
    }


# =====================================================
# Request-to-Plan File Binding
# =====================================================

_FILE_CREATION_VERBS = (
    "create",
    "make",
    "save",
    "write",
)


def _extract_explicit_requested_filename(user_request):
    """
    Extract a filename explicitly written by the user in
    a likely file-creation request.

    The exact token is preserved so unsafe path syntax cannot
    be silently rewritten by the planner before validation.
    """

    request = str(
        user_request
    ).strip()

    request_lower = request.lower()

    has_creation_verb = any(
        re.search(
            rf"\b{re.escape(verb)}\b",
            request_lower,
        )
        for verb in _FILE_CREATION_VERBS
    )

    if not has_creation_verb:
        return None

    match = re.search(
        r"(?i)(?<!\w)((?:[a-z]:[\\/])?[^\s\"'<>|?*]+\.[a-z0-9]{1,10})",
        request,
    )

    if not match:
        return None

    filename = (
        match.group(1)
        .strip()
        .rstrip(".,;!?)]}")
    )

    return filename or None


def validate_plan_against_request(
    plan,
    user_request,
):
    """
    Bind explicit file-creation requests to the exact filename
    supplied by the user.

    This prevents an unsafe request such as ../escape.txt from
    being silently rewritten to escape.txt before validation.
    """

    explicit_filename = (
        _extract_explicit_requested_filename(
            user_request
        )
    )

    if not explicit_filename:
        return plan

    # Validate the exact filename from the user's request
    # through the central registry policy.
    validate_tool_args(
        "create_file",
        {
            "filename": explicit_filename,
            "text": "request-validation-placeholder",
        },
    )

    file_write_steps = [
        step
        for step in plan.get(
            "steps",
            [],
        )
        if step.get(
            "action"
        ) in {
            "create_file",
            "append_file",
        }
    ]

    if not file_write_steps:
        return plan

    for step in file_write_steps:
        planned_filename = str(
            step.get(
                "args",
                {},
            ).get(
                "filename",
                "",
            )
        ).strip()

        if (
            planned_filename.casefold()
            != explicit_filename.casefold()
        ):
            raise ValueError(
                "Planner changed the requested filename from "
                f"'{explicit_filename}' to "
                f"'{planned_filename}'. "
                "EV refuses to silently rewrite requested "
                "file paths or filenames."
            )

    return plan


# =====================================================
# JSON Parsing
# =====================================================

def _extract_json_object(text):
    """
    Best-effort recovery when a model adds a small amount
    of text around an otherwise valid JSON object.
    """

    text = str(
        text
    ).strip()

    if not text:
        raise ValueError(
            "Planner returned an empty response."
        )

    if text.startswith("```"):
        text = text.replace(
            "```json",
            "",
            1,
        )

        text = text.replace(
            "```",
            "",
        )

        text = text.strip()

    first_brace = text.find(
        "{"
    )

    last_brace = text.rfind(
        "}"
    )

    if (
        first_brace == -1
        or last_brace == -1
        or last_brace < first_brace
    ):
        raise ValueError(
            "Planner returned invalid JSON."
        )

    return text[
        first_brace:
        last_brace + 1
    ]


def parse_planner_response(text):
    json_text = _extract_json_object(
        text
    )

    try:
        plan = json.loads(
            json_text
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Planner returned invalid JSON."
        ) from exc

    return validate_plan(
        plan
    )


# =====================================================
# NVIDIA Planner Call
# =====================================================

def create_plan(
    client,
    model,
    user_request,
):
    user_request = str(
        user_request
    ).strip()

    if not user_request:
        raise ValueError(
            "No task was provided to the planner."
        )

    response = (
        client
        .chat
        .completions
        .create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": PLANNER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_request,
                },
            ],
            temperature=0.1,
            max_tokens=600,
        )
    )

    raw_plan = (
        response
        .choices[0]
        .message
        .content
        or ""
    )

    plan = parse_planner_response(
        raw_plan
    )

    return validate_plan_against_request(
        plan,
        user_request,
    )


# =====================================================
# Terminal Formatting
# =====================================================

def format_plan(plan):
    validated_plan = validate_plan(
        plan
    )

    lines = [
        f"Goal: {validated_plan['goal']}",
    ]

    steps = validated_plan[
        "steps"
    ]

    if not steps:
        lines.append(
            "No approved actions available for this request."
        )

        return "\n".join(
            lines
        )

    for index, step in enumerate(
        steps,
        start=1,
    ):
        action = step[
            "action"
        ]

        args = step[
            "args"
        ]

        if args:
            lines.append(
                f"{index}. {action} -> {args}"
            )
        else:
            lines.append(
                f"{index}. {action}"
            )

    return "\n".join(
        lines
    )


# =====================================================
# Local Test
# =====================================================

if __name__ == "__main__":
    print(
        "EV v0.9 Safe Task Planner"
    )

    print(
        "Allowed actions from tool_registry.py:"
    )

    for action in get_allowed_actions():
        print(
            f"- {action}"
        )
