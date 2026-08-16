from planner import validate_plan

from pc_tools import (
    get_current_time,
    get_current_date,
    open_data_folder,
    launch_app,
    calculate,
    open_notepad_and_type,
)


MAX_GENERATED_TEXT_CHARS = 3500


# =====================================================
# EV v0.8 Safe Plan Executor
# =====================================================

def generate_text(
    client,
    model,
    prompt,
):
    """
    Generate plain text for a validated planner step.

    Generated text is data only. It is never executed as code,
    shell commands, or another tool instruction.
    """

    prompt = str(
        prompt
    ).strip()

    if not prompt:
        raise ValueError(
            "No generation prompt was provided."
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
                    "content": (
                        "You are EV's safe task content generator. "
                        "Generate useful plain text for the user's "
                        "approved task. Return plain text only. "
                        "Do not claim that computer actions happened. "
                        "Do not output tool calls or JSON. "
                        "Keep the result concise unless the prompt "
                        "asks for detail."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.5,
            max_tokens=600,
        )
    )

    generated_text = (
        response
        .choices[0]
        .message
        .content
        or ""
    ).strip()

    if not generated_text:
        raise RuntimeError(
            "The text generator returned an empty response."
        )

    if (
        len(generated_text)
        > MAX_GENERATED_TEXT_CHARS
    ):
        generated_text = generated_text[
            :MAX_GENERATED_TEXT_CHARS
        ].rstrip()

    return generated_text


def execute_plan(
    client,
    model,
    plan,
):
    """
    Execute a plan only after planner.py validates it.

    This function contains an explicit action dispatch table.
    Unknown actions never execute.
    """

    validated_plan = validate_plan(
        plan
    )

    if not validated_plan["steps"]:
        return {
            "goal": validated_plan["goal"],
            "executed": False,
            "steps": [],
        }

    state = {
        "generated_text": None,
    }

    execution_steps = []

    for index, step in enumerate(
        validated_plan["steps"],
        start=1,
    ):
        action = step[
            "action"
        ]

        args = step[
            "args"
        ]

        if action == "get_time":
            current_time = get_current_time()

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": (
                        f"The current local time is "
                        f"{current_time}."
                    ),
                }
            )

            continue

        if action == "get_date":
            current_date = get_current_date()

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": (
                        f"Today is {current_date}."
                    ),
                }
            )

            continue

        if action == "calculate":
            expression = args[
                "expression"
            ]

            result = calculate(
                expression
            )

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": (
                        f"{expression} = {result}."
                    ),
                }
            )

            continue

        if action == "open_app":
            result = launch_app(
                args["app"]
            )

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": result,
                }
            )

            continue

        if action == "open_data_folder":
            result = open_data_folder()

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": result,
                }
            )

            continue

        if action == "generate_text":
            generated_text = generate_text(
                client,
                model,
                args["prompt"],
            )

            state[
                "generated_text"
            ] = generated_text

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": (
                        "Generated the requested text."
                    ),
                    "output": generated_text,
                }
            )

            continue

        if action == "write_notepad":
            if "text" in args:
                notepad_text = args[
                    "text"
                ]

                source = "literal"

            else:
                notepad_text = state.get(
                    "generated_text"
                )

                source = "generated_text"

                if not notepad_text:
                    raise RuntimeError(
                        "No generated text is available "
                        "for the Notepad step."
                    )

            result = open_notepad_and_type(
                notepad_text
            )

            execution_steps.append(
                {
                    "number": index,
                    "action": action,
                    "summary": result,
                    "source": source,
                }
            )

            continue

        # Defense in depth. validate_plan() should already
        # prevent this branch from ever being reached.
        raise ValueError(
            f"Executor refused unknown action "
            f"'{action}'."
        )

    return {
        "goal": validated_plan["goal"],
        "executed": True,
        "steps": execution_steps,
    }


def format_execution_report(report):
    """
    Build a readable terminal report without pretending
    that a step succeeded unless execute_plan completed it.
    """

    if not report.get(
        "executed"
    ):
        return (
            "No actions were executed."
        )

    lines = []

    steps = report.get(
        "steps",
        []
    )

    has_notepad_generated_write = any(
        step.get("action")
        == "write_notepad"
        and step.get("source")
        == "generated_text"
        for step in steps
    )

    for step in steps:
        number = step[
            "number"
        ]

        action = step[
            "action"
        ]

        summary = step[
            "summary"
        ]

        if (
            action == "generate_text"
            and not has_notepad_generated_write
        ):
            output = step.get(
                "output",
                "",
            )

            lines.append(
                f"{number}. {action}: {summary}"
            )

            if output:
                lines.append(
                    output
                )

        else:
            lines.append(
                f"{number}. {action}: {summary}"
            )

    return "\n".join(
        lines
    )
