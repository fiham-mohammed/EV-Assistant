from planner import validate_plan

from tool_registry import (
    GENERATED_TEXT_SOURCE,
    get_allowed_actions,
)

from file_write_tools import (
    create_text_file,
    append_text_file,
)

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
# EV v0.9 Registry-Backed Safe Plan Executor
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


# =====================================================
# Action Handlers
# =====================================================

def _handle_get_time(
    client,
    model,
    args,
    state,
):
    current_time = get_current_time()

    return {
        "summary": (
            f"The current local time is "
            f"{current_time}."
        ),
    }


def _handle_get_date(
    client,
    model,
    args,
    state,
):
    current_date = get_current_date()

    return {
        "summary": (
            f"Today is {current_date}."
        ),
    }


def _handle_calculate(
    client,
    model,
    args,
    state,
):
    expression = args[
        "expression"
    ]

    result = calculate(
        expression
    )

    return {
        "summary": (
            f"{expression} = {result}."
        ),
    }


def _handle_open_app(
    client,
    model,
    args,
    state,
):
    result = launch_app(
        args[
            "app"
        ]
    )

    return {
        "summary": result,
    }


def _handle_open_data_folder(
    client,
    model,
    args,
    state,
):
    result = open_data_folder()

    return {
        "summary": result,
    }


def _handle_generate_text(
    client,
    model,
    args,
    state,
):
    generated_text = generate_text(
        client,
        model,
        args[
            "prompt"
        ],
    )

    state[
        GENERATED_TEXT_SOURCE
    ] = generated_text

    return {
        "summary": (
            "Generated the requested text."
        ),
        "output": generated_text,
    }


def _handle_append_file(
    client,
    model,
    args,
    state,
):
    if "text" in args:
        file_text = args[
            "text"
        ]

        source = "literal"

    else:
        file_text = state.get(
            GENERATED_TEXT_SOURCE
        )

        source = GENERATED_TEXT_SOURCE

        if file_text is None:
            raise RuntimeError(
                "No generated text is available "
                "for the file append step."
            )

    result = append_text_file(
        args[
            "filename"
        ],
        file_text,
    )

    return {
        "summary": result,
        "source": source,
    }


def _handle_create_file(
    client,
    model,
    args,
    state,
):
    if "text" in args:
        file_text = args[
            "text"
        ]

        source = "literal"

    else:
        file_text = state.get(
            GENERATED_TEXT_SOURCE
        )

        source = GENERATED_TEXT_SOURCE

        if file_text is None:
            raise RuntimeError(
                "No generated text is available "
                "for the file creation step."
            )

    result = create_text_file(
        args[
            "filename"
        ],
        file_text,
    )

    return {
        "summary": result,
        "source": source,
    }


def _handle_write_notepad(
    client,
    model,
    args,
    state,
):
    if "text" in args:
        notepad_text = args[
            "text"
        ]

        source = "literal"

    else:
        notepad_text = state.get(
            GENERATED_TEXT_SOURCE
        )

        source = GENERATED_TEXT_SOURCE

        if not notepad_text:
            raise RuntimeError(
                "No generated text is available "
                "for the Notepad step."
            )

    result = open_notepad_and_type(
        notepad_text
    )

    return {
        "summary": result,
        "source": source,
    }


# =====================================================
# Explicit Executor Dispatch Table
# =====================================================

ACTION_HANDLERS = {
    "append_file": _handle_append_file,
    "create_file": _handle_create_file,
    "get_time": _handle_get_time,
    "get_date": _handle_get_date,
    "calculate": _handle_calculate,
    "open_app": _handle_open_app,
    "open_data_folder": _handle_open_data_folder,
    "generate_text": _handle_generate_text,
    "write_notepad": _handle_write_notepad,
}


def validate_executor_registry_alignment():
    """
    Defense in depth:
    every registry action must have exactly one explicit
    executor handler, and the executor must not expose
    handlers for actions absent from the registry.
    """

    registry_actions = set(
        get_allowed_actions()
    )

    executor_actions = set(
        ACTION_HANDLERS
    )

    missing_handlers = (
        registry_actions
        - executor_actions
    )

    extra_handlers = (
        executor_actions
        - registry_actions
    )

    if missing_handlers:
        raise RuntimeError(
            "Executor is missing handlers for: "
            + ", ".join(
                sorted(
                    missing_handlers
                )
            )
        )

    if extra_handlers:
        raise RuntimeError(
            "Executor contains unregistered handlers for: "
            + ", ".join(
                sorted(
                    extra_handlers
                )
            )
        )

    return True


# Check registry/handler alignment immediately at import time.
validate_executor_registry_alignment()


# =====================================================
# Plan Execution
# =====================================================

def execute_plan(
    client,
    model,
    plan,
):
    """
    Execute only a fully validated plan.

    Planner validation delegates tool policy to tool_registry.py.
    The executor then dispatches each approved action through
    the fixed ACTION_HANDLERS table above.
    """

    validated_plan = validate_plan(
        plan
    )

    if not validated_plan[
        "steps"
    ]:
        return {
            "goal": validated_plan[
                "goal"
            ],
            "executed": False,
            "steps": [],
        }

    state = {
        GENERATED_TEXT_SOURCE: None,
    }

    execution_steps = []

    for index, step in enumerate(
        validated_plan[
            "steps"
        ],
        start=1,
    ):
        action = step[
            "action"
        ]

        args = step[
            "args"
        ]

        handler = ACTION_HANDLERS.get(
            action
        )

        # Defense in depth. The registry and alignment check
        # should make this unreachable.
        if handler is None:
            raise ValueError(
                f"Executor refused unknown action "
                f"'{action}'."
            )

        handler_result = handler(
            client,
            model,
            args,
            state,
        )

        if not isinstance(
            handler_result,
            dict,
        ):
            raise RuntimeError(
                f"Executor handler '{action}' "
                "returned an invalid result."
            )

        summary = handler_result.get(
            "summary"
        )

        if not isinstance(
            summary,
            str,
        ) or not summary.strip():
            raise RuntimeError(
                f"Executor handler '{action}' "
                "did not return a valid summary."
            )

        execution_step = {
            "number": index,
            "action": action,
            "summary": summary.strip(),
        }

        for optional_key in (
            "output",
            "source",
        ):
            if optional_key in handler_result:
                execution_step[
                    optional_key
                ] = handler_result[
                    optional_key
                ]

        execution_steps.append(
            execution_step
        )

    return {
        "goal": validated_plan[
            "goal"
        ],
        "executed": True,
        "steps": execution_steps,
    }


# =====================================================
# Execution Report
# =====================================================

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

    has_generated_text_consumer = any(
        step.get(
            "action"
        ) in {
            "write_notepad",
            "create_file",
            "append_file",
        }
        and step.get(
            "source"
        ) == GENERATED_TEXT_SOURCE
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
            and not has_generated_text_consumer
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


# =====================================================
# Local Test
# =====================================================

if __name__ == "__main__":
    print(
        "EV v0.9 Registry-Backed Executor"
    )

    print(
        "Registry alignment: PASS"
    )

    print(
        "Registered executor actions:"
    )

    for action in sorted(
        ACTION_HANDLERS
    ):
        print(
            f"- {action}"
        )
