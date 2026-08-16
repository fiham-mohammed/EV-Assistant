import json


# =====================================================
# EV v0.8 Safe Task Planner
# =====================================================

MAX_PLAN_STEPS = 8
MAX_TEXT_ARG_CHARS = 4000
MAX_EXPRESSION_CHARS = 200

ALLOWED_APPS = {
    "notepad",
    "calculator",
}

ALLOWED_ACTIONS = {
    "get_time",
    "get_date",
    "calculate",
    "open_app",
    "open_data_folder",
    "write_notepad",
    "generate_text",
}


PLANNER_SYSTEM_PROMPT = """
You are EV's safe task planner.

Your job is to convert a user's request into a short JSON plan.

You DO NOT execute actions.

Allowed actions:

1. get_time
   args:
   {}

2. get_date
   args:
   {}

3. calculate
   args:
   {
     "expression": "2+2"
   }

4. open_app
   args:
   {
     "app": "notepad"
   }

   Approved apps:
   - notepad
   - calculator

5. open_data_folder
   args:
   {}

6. generate_text
   args:
   {
     "prompt": "what text should be generated"
   }

7. write_notepad

   For literal text:
   {
     "text": "plain text to type"
   }

   For text produced by a previous generate_text step:
   {
     "source": "generated_text"
   }

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
- Only use approved applications.
- Keep plans short.
- Use lowercase action names.
- Use the exact argument names shown above.
- If the user's request cannot be completed using ONLY the allowed actions,
  return an empty steps list.
- Do not explain rejected requests outside the JSON.

Notepad rules:

- write_notepad already opens/focuses approved Notepad.
- Do NOT add open_app for Notepad when the plan also uses write_notepad.
- If the user asks to type literal text, use write_notepad with "text".
- If the user asks EV to create, explain, describe, prepare, draft, or write
  new content in Notepad, first use generate_text and then use write_notepad
  with {"source": "generated_text"}.
- Never put placeholder phrases such as "generated text",
  "AI study plan text", or "content goes here" in write_notepad.
- If generate_text is used for Notepad, write_notepad must reference
  "generated_text".

Return exactly this general structure:

{
  "goal": "short description of the user's goal",
  "steps": [
    {
      "action": "allowed_action_name",
      "args": {}
    }
  ]
}

Example: get time

User:
What time is it?

Response:
{
  "goal": "Get the current local time",
  "steps": [
    {
      "action": "get_time",
      "args": {}
    }
  ]
}

Example: literal Notepad typing

User:
Open Notepad and type hello world

Response:
{
  "goal": "Type hello world in Notepad",
  "steps": [
    {
      "action": "write_notepad",
      "args": {
        "text": "hello world"
      }
    }
  ]
}

Example: AI-generated Notepad writing

User:
Open Notepad and create a short AI study plan

Response:
{
  "goal": "Create a short AI study plan in Notepad",
  "steps": [
    {
      "action": "generate_text",
      "args": {
        "prompt": "Create a short practical AI study plan"
      }
    },
    {
      "action": "write_notepad",
      "args": {
        "source": "generated_text"
      }
    }
  ]
}

Example: unsupported request

User:
Run a PowerShell command

Response:
{
  "goal": "Unsupported request",
  "steps": []
}
""".strip()


def _require_exact_keys(
    args,
    expected_keys,
    action,
):
    actual_keys = set(
        args.keys()
    )

    expected_keys = set(
        expected_keys
    )

    if actual_keys != expected_keys:
        raise ValueError(
            f"Action '{action}' requires args "
            f"{sorted(expected_keys)}."
        )


def _require_string(
    value,
    field_name,
    max_chars,
):
    if not isinstance(
        value,
        str,
    ):
        raise ValueError(
            f"Planner field '{field_name}' "
            "must be a string."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"Planner field '{field_name}' "
            "cannot be empty."
        )

    if len(value) > max_chars:
        raise ValueError(
            f"Planner field '{field_name}' "
            "is too long."
        )

    return value


def validate_step_args(
    action,
    args,
):
    if not isinstance(
        args,
        dict,
    ):
        raise ValueError(
            "Planner step args must be an object."
        )

    if action in {
        "get_time",
        "get_date",
        "open_data_folder",
    }:
        _require_exact_keys(
            args,
            set(),
            action,
        )

        return

    if action == "calculate":
        _require_exact_keys(
            args,
            {"expression"},
            action,
        )

        _require_string(
            args["expression"],
            "expression",
            MAX_EXPRESSION_CHARS,
        )

        return

    if action == "open_app":
        _require_exact_keys(
            args,
            {"app"},
            action,
        )

        app = _require_string(
            args["app"],
            "app",
            50,
        ).lower()

        if app not in ALLOWED_APPS:
            approved = ", ".join(
                sorted(ALLOWED_APPS)
            )

            raise ValueError(
                f"Planner app '{app}' is not approved. "
                f"Approved apps: {approved}"
            )

        return

    if action == "write_notepad":
        keys = set(
            args.keys()
        )

        if keys == {"text"}:
            _require_string(
                args["text"],
                "text",
                MAX_TEXT_ARG_CHARS,
            )

            return

        if keys == {"source"}:
            source = _require_string(
                args["source"],
                "source",
                50,
            ).lower()

            if source != "generated_text":
                raise ValueError(
                    "write_notepad source must be "
                    "'generated_text'."
                )

            return

        raise ValueError(
            "Action 'write_notepad' requires either "
            "{'text': ...} or "
            "{'source': 'generated_text'}."
        )

    if action == "generate_text":
        _require_exact_keys(
            args,
            {"prompt"},
            action,
        )

        _require_string(
            args["prompt"],
            "prompt",
            MAX_TEXT_ARG_CHARS,
        )

        return

    raise ValueError(
        f"Planner action '{action}' "
        "has no argument validator."
    )


def validate_plan(plan):
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

    goal = _require_string(
        plan["goal"],
        "goal",
        300,
    )

    steps = plan["steps"]

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

    normalized_steps = []
    generated_text_available = False

    for index, step in enumerate(
        steps,
        start=1,
    ):
        if not isinstance(
            step,
            dict,
        ):
            raise ValueError(
                f"Planner step {index} "
                "must be an object."
            )

        if set(step.keys()) != {
            "action",
            "args",
        }:
            raise ValueError(
                f"Planner step {index} must contain "
                "only 'action' and 'args'."
            )

        action = step["action"]

        if not isinstance(
            action,
            str,
        ):
            raise ValueError(
                f"Planner step {index} action "
                "must be a string."
            )

        action = (
            action
            .strip()
            .lower()
        )

        if action not in ALLOWED_ACTIONS:
            raise ValueError(
                f"Planner action '{action}' "
                "is not allowed."
            )

        args = step["args"]

        validate_step_args(
            action,
            args,
        )

        normalized_args = dict(
            args
        )

        if action == "open_app":
            normalized_args["app"] = (
                normalized_args["app"]
                .strip()
                .lower()
            )

        if action == "generate_text":
            generated_text_available = True

        if action == "write_notepad":
            if "source" in normalized_args:
                normalized_args["source"] = (
                    normalized_args["source"]
                    .strip()
                    .lower()
                )

                if not generated_text_available:
                    raise ValueError(
                        "write_notepad cannot use "
                        "'generated_text' before a "
                        "generate_text step."
                    )

        normalized_steps.append(
            {
                "action": action,
                "args": normalized_args,
            }
        )

    # Canonicalize a harmless planner redundancy:
    # write_notepad already launches/focuses approved Notepad,
    # so a separate open_app("notepad") step is unnecessary.
    has_notepad_write = any(
        step["action"] == "write_notepad"
        for step in normalized_steps
    )

    if has_notepad_write:
        normalized_steps = [
            step
            for step in normalized_steps
            if not (
                step["action"] == "open_app"
                and step["args"].get("app") == "notepad"
            )
        ]

    return {
        "goal": goal,
        "steps": normalized_steps,
    }


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

    return parse_planner_response(
        raw_plan
    )


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


if __name__ == "__main__":
    print(
        "EV v0.8 Safe Task Planner"
    )

    print(
        "Allowed actions:"
    )

    for action in sorted(
        ALLOWED_ACTIONS
    ):
        print(
            f"- {action}"
        )
