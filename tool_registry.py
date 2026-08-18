from pathlib import Path

# =====================================================
# EV v0.9 Central Tool Registry
# =====================================================

MAX_PLAN_STEPS = 8
MAX_TEXT_ARG_CHARS = 4000
MAX_EXPRESSION_CHARS = 200

GENERATED_TEXT_SOURCE = "generated_text"

APPROVED_FILE_EXTENSIONS = frozenset(
    {
        ".txt",
        ".md",
    }
)

MAX_SAFE_FILENAME_CHARS = 120

APPROVED_APPS = frozenset(
    {
        "notepad",
        "calculator",
    }
)


# =====================================================
# Tool Definitions
# =====================================================

TOOL_REGISTRY = {
    "get_time": {
        "description": "Get the real current local time.",
        "args": {},
    },

    "get_date": {
        "description": "Get the real current local date.",
        "args": {},
    },

    "calculate": {
        "description": (
            "Safely evaluate an approved arithmetic expression."
        ),
        "args": {
            "expression": {
                "type": "string",
                "required": True,
                "max_chars": MAX_EXPRESSION_CHARS,
            },
        },
    },

    "open_app": {
        "description": (
            "Launch an application from EV's approved app allowlist."
        ),
        "args": {
            "app": {
                "type": "enum",
                "required": True,
                "values": tuple(
                    sorted(
                        APPROVED_APPS
                    )
                ),
            },
        },
    },

    "open_data_folder": {
        "description": (
            "Open EV's approved local data folder."
        ),
        "args": {},
    },

    "generate_text": {
        "description": (
            "Generate plain text for an approved task."
        ),
        "args": {
            "prompt": {
                "type": "string",
                "required": True,
                "max_chars": MAX_TEXT_ARG_CHARS,
            },
        },
    },

    "append_file": {
        "description": (
            "Append text to an existing approved .txt or .md file "
            "inside EV's data folder without overwriting it."
        ),
        "arg_variants": (
            {
                "filename": {
                    "type": "filename",
                    "required": True,
                    "max_chars": MAX_SAFE_FILENAME_CHARS,
                    "extensions": tuple(
                        sorted(
                            APPROVED_FILE_EXTENSIONS
                        )
                    ),
                },
                "text": {
                    "type": "string",
                    "required": True,
                    "max_chars": MAX_TEXT_ARG_CHARS,
                },
            },
            {
                "filename": {
                    "type": "filename",
                    "required": True,
                    "max_chars": MAX_SAFE_FILENAME_CHARS,
                    "extensions": tuple(
                        sorted(
                            APPROVED_FILE_EXTENSIONS
                        )
                    ),
                },
                "source": {
                    "type": "enum",
                    "required": True,
                    "values": (
                        GENERATED_TEXT_SOURCE,
                    ),
                },
            },
        ),
    },

    "create_file": {
        "description": (
            "Create a new approved .txt or .md file inside "
            "EV's data folder without overwriting existing files."
        ),
        "arg_variants": (
            {
                "filename": {
                    "type": "filename",
                    "required": True,
                    "max_chars": MAX_SAFE_FILENAME_CHARS,
                    "extensions": tuple(
                        sorted(
                            APPROVED_FILE_EXTENSIONS
                        )
                    ),
                },
                "text": {
                    "type": "string",
                    "required": True,
                    "max_chars": MAX_TEXT_ARG_CHARS,
                },
            },
            {
                "filename": {
                    "type": "filename",
                    "required": True,
                    "max_chars": MAX_SAFE_FILENAME_CHARS,
                    "extensions": tuple(
                        sorted(
                            APPROVED_FILE_EXTENSIONS
                        )
                    ),
                },
                "source": {
                    "type": "enum",
                    "required": True,
                    "values": (
                        GENERATED_TEXT_SOURCE,
                    ),
                },
            },
        ),
    },

    "write_notepad": {
        "description": (
            "Open/focus approved Notepad and type literal "
            "or previously generated text."
        ),
        "arg_variants": (
            {
                "text": {
                    "type": "string",
                    "required": True,
                    "max_chars": MAX_TEXT_ARG_CHARS,
                },
            },
            {
                "source": {
                    "type": "enum",
                    "required": True,
                    "values": (
                        GENERATED_TEXT_SOURCE,
                    ),
                },
            },
        ),
    },
}


# =====================================================
# Registry Helpers
# =====================================================

def get_allowed_actions():
    """
    Return approved planner/executor action names
    in deterministic order.
    """

    return tuple(
        sorted(
            TOOL_REGISTRY
        )
    )


def is_allowed_action(action):
    if not isinstance(
        action,
        str,
    ):
        return False

    return (
        action
        .strip()
        .lower()
        in TOOL_REGISTRY
    )


def normalize_action_name(action):
    if not isinstance(
        action,
        str,
    ):
        raise ValueError(
            "Tool action must be a string."
        )

    normalized = (
        action
        .strip()
        .lower()
    )

    if not normalized:
        raise ValueError(
            "Tool action cannot be empty."
        )

    if normalized not in TOOL_REGISTRY:
        raise ValueError(
            f"Tool action '{normalized}' is not approved."
        )

    return normalized


def get_tool_definition(action):
    normalized = normalize_action_name(
        action
    )

    return TOOL_REGISTRY[
        normalized
    ]


# =====================================================
# Argument Validation
# =====================================================

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
            f"Tool argument '{field_name}' must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"Tool argument '{field_name}' cannot be empty."
        )

    if len(normalized) > max_chars:
        raise ValueError(
            f"Tool argument '{field_name}' is too long."
        )

    return normalized


def _validate_schema(
    action,
    args,
    schema,
):
    expected_keys = set(
        schema.keys()
    )

    actual_keys = set(
        args.keys()
    )

    if actual_keys != expected_keys:
        raise ValueError(
            f"Action '{action}' requires args "
            f"{sorted(expected_keys)}."
        )

    normalized_args = {}

    for field_name, rule in schema.items():
        value = args[
            field_name
        ]

        field_type = rule[
            "type"
        ]

        if field_type == "string":
            normalized_args[
                field_name
            ] = _require_string(
                value,
                field_name,
                rule[
                    "max_chars"
                ],
            )

            continue

        if field_type == "enum":
            normalized_value = _require_string(
                value,
                field_name,
                100,
            ).lower()

            allowed_values = set(
                rule[
                    "values"
                ]
            )

            if normalized_value not in allowed_values:
                approved = ", ".join(
                    sorted(
                        allowed_values
                    )
                )

                raise ValueError(
                    f"Tool argument '{field_name}' value "
                    f"'{normalized_value}' is not approved. "
                    f"Approved values: {approved}"
                )

            normalized_args[
                field_name
            ] = normalized_value

            continue

        if field_type == "filename":
            normalized_value = _require_string(
                value,
                field_name,
                rule[
                    "max_chars"
                ],
            )

            if (
                "/" in normalized_value
                or "\\" in normalized_value
                or ":" in normalized_value
                or normalized_value in {
                    ".",
                    "..",
                }
            ):
                raise ValueError(
                    "Filename must be a simple file name "
                    "without directories or drive prefixes."
                )

            filename_path = Path(
                normalized_value
            )

            if (
                filename_path.is_absolute()
                or filename_path.name
                != normalized_value
            ):
                raise ValueError(
                    "Filename must stay inside "
                    "EV's approved data folder."
                )

            extension = (
                filename_path.suffix
                .lower()
            )

            allowed_extensions = set(
                rule[
                    "extensions"
                ]
            )

            if extension not in allowed_extensions:
                approved = ", ".join(
                    sorted(
                        allowed_extensions
                    )
                )

                raise ValueError(
                    f"File type '{extension or '(none)'}' "
                    f"is not approved. "
                    f"Approved types: {approved}"
                )

            normalized_args[
                field_name
            ] = normalized_value

            continue

        raise ValueError(
            f"Unsupported registry field type "
            f"'{field_type}'."
        )

    return normalized_args


def validate_tool_args(
    action,
    args,
):
    """
    Validate and normalize arguments for one approved action.

    This function does not execute anything.
    """

    normalized_action = normalize_action_name(
        action
    )

    if not isinstance(
        args,
        dict,
    ):
        raise ValueError(
            "Tool args must be an object."
        )

    definition = TOOL_REGISTRY[
        normalized_action
    ]

    if "args" in definition:
        return _validate_schema(
            normalized_action,
            args,
            definition[
                "args"
            ],
        )

    variants = definition.get(
        "arg_variants",
        (),
    )

    validation_errors = []

    for schema in variants:
        try:
            return _validate_schema(
                normalized_action,
                args,
                schema,
            )

        except ValueError as exc:
            validation_errors.append(
                str(exc)
            )

    raise ValueError(
        f"Arguments for action '{normalized_action}' "
        "do not match any approved schema."
    )


# =====================================================
# Step Validation
# =====================================================

def normalize_tool_step(step):
    """
    Validate one planner step and return a normalized copy.
    """

    if not isinstance(
        step,
        dict,
    ):
        raise ValueError(
            "Planner step must be an object."
        )

    if set(step.keys()) != {
        "action",
        "args",
    }:
        raise ValueError(
            "Planner step must contain only "
            "'action' and 'args'."
        )

    action = normalize_action_name(
        step[
            "action"
        ]
    )

    args = validate_tool_args(
        action,
        step[
            "args"
        ],
    )

    return {
        "action": action,
        "args": args,
    }


def normalize_plan_steps(steps):
    """
    Validate step schemas, enforce simple dependencies,
    and canonicalize safe planner redundancies.

    This function does not execute anything.
    """

    if not isinstance(
        steps,
        list,
    ):
        raise ValueError(
            "Planner steps must be a list."
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
        try:
            normalized_step = normalize_tool_step(
                step
            )

        except ValueError as exc:
            raise ValueError(
                f"Planner step {index} is invalid: {exc}"
            ) from exc

        action = normalized_step[
            "action"
        ]

        args = normalized_step[
            "args"
        ]

        if action == "generate_text":
            generated_text_available = True

        # Canonicalize a common planner formatting mistake.
        # If generated text is already available, then:
        # {"text": "generated_text"}
        # means the same approved data flow as:
        # {"source": "generated_text"}.
        if (
            action in {
                "write_notepad",
                "create_file",
                "append_file",
            }
            and generated_text_available
            and isinstance(
                args.get(
                    "text"
                ),
                str,
            )
            and args[
                "text"
            ].strip().lower()
            == GENERATED_TEXT_SOURCE
        ):
            args = {
                "source": GENERATED_TEXT_SOURCE,
            }

            normalized_step = {
                "action": action,
                "args": args,
            }

        if (
            action in {
                "write_notepad",
                "create_file",
                "append_file",
            }
            and args.get(
                "source"
            ) == GENERATED_TEXT_SOURCE
            and not generated_text_available
        ):
            raise ValueError(
                f"{action} cannot use "
                "'generated_text' before a "
                "generate_text step."
            )

        normalized_steps.append(
            normalized_step
        )

    # Remove an unused generate_text step when the plan
    # contains a concrete text destination but none of those
    # destinations consume generated_text.
    #
    # Example:
    #   generate_text(...)
    #   create_file({"text": "hello"})
    #
    # The generation result is unused, so running it would
    # only waste an AI call and clutter the execution report.
    output_actions = {
        "write_notepad",
        "create_file",
        "append_file",
    }

    has_output_action = any(
        step[
            "action"
        ] in output_actions
        for step in normalized_steps
    )

    has_generated_text_consumer = any(
        step[
            "action"
        ] in output_actions
        and step[
            "args"
        ].get(
            "source"
        ) == GENERATED_TEXT_SOURCE
        for step in normalized_steps
    )

    if (
        has_output_action
        and not has_generated_text_consumer
    ):
        normalized_steps = [
            step
            for step in normalized_steps
            if step[
                "action"
            ] != "generate_text"
        ]

    # write_notepad already launches/focuses Notepad.
    # Remove a redundant open_app(notepad) step if the
    # model happens to include both.
    has_notepad_write = any(
        step[
            "action"
        ] == "write_notepad"
        for step in normalized_steps
    )

    if has_notepad_write:
        normalized_steps = [
            step
            for step in normalized_steps
            if not (
                step[
                    "action"
                ] == "open_app"
                and step[
                    "args"
                ].get(
                    "app"
                ) == "notepad"
            )
        ]

    return normalized_steps


# =====================================================
# Planner Prompt Reference
# =====================================================

def build_planner_action_reference():
    """
    Build a deterministic human-readable reference that can
    later be inserted into EV's planner system prompt.
    """

    lines = [
        "Allowed actions:",
        "",
    ]

    for action in get_allowed_actions():
        definition = TOOL_REGISTRY[
            action
        ]

        lines.append(
            f"- {action}: "
            f"{definition['description']}"
        )

        if "args" in definition:
            schema = definition[
                "args"
            ]

            if not schema:
                lines.append(
                    "  args: {}"
                )

            else:
                fields = ", ".join(
                    schema.keys()
                )

                lines.append(
                    f"  args fields: {fields}"
                )

        else:
            variants = definition.get(
                "arg_variants",
                ()
            )

            variant_text = " OR ".join(
                ", ".join(
                    schema.keys()
                )
                for schema in variants
            )

            lines.append(
                f"  args variants: {variant_text}"
            )

    return "\n".join(
        lines
    )


# =====================================================
# Local Test
# =====================================================

if __name__ == "__main__":
    print(
        "EV v0.9 Tool Registry"
    )

    print()

    print(
        build_planner_action_reference()
    )
