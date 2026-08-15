import ast
import os
import operator
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pyautogui


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

APP_ALLOWLIST = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
}

APP_ALIASES = {
    "notepad": "notepad",
    "calculator": "calculator",
    "calc": "calculator",
}

MAX_NOTEPAD_TYPE_CHARS = 5000


def get_current_time():
    return datetime.now().strftime("%I:%M %p")


def get_current_date():
    return datetime.now().strftime("%A, %d %B %Y")


def open_data_folder():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    os.startfile(
        DATA_DIR
    )

    return (
        "Opened EV's approved data folder."
    )


def normalize_app_name(app_name):
    normalized = (
        app_name
        .strip()
        .lower()
    )

    return APP_ALIASES.get(
        normalized,
        normalized,
    )


def launch_app(app_name):
    normalized_name = normalize_app_name(
        app_name
    )

    executable = APP_ALLOWLIST.get(
        normalized_name
    )

    if not executable:
        approved = ", ".join(
            sorted(APP_ALLOWLIST)
        )

        raise ValueError(
            f"App '{app_name}' is not approved. "
            f"Approved apps: {approved}"
        )

    subprocess.Popen(
        [executable]
    )

    return (
        f"Launched {normalized_name}."
    )


_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

MAX_ABS_RESULT = 1_000_000_000_000_000
MAX_ABS_EXPONENT = 12


def _evaluate_math_node(node):
    if isinstance(node, ast.Expression):
        return _evaluate_math_node(
            node.body
        )

    if isinstance(node, ast.Constant):
        if isinstance(
            node.value,
            (int, float),
        ):
            return node.value

        raise ValueError(
            "Only numeric values are allowed."
        )

    if isinstance(node, ast.UnaryOp):
        operator_function = (
            _ALLOWED_UNARY_OPERATORS.get(
                type(node.op)
            )
        )

        if operator_function is None:
            raise ValueError(
                "Unsupported unary operator."
            )

        return operator_function(
            _evaluate_math_node(
                node.operand
            )
        )

    if isinstance(node, ast.BinOp):
        operator_function = (
            _ALLOWED_BINARY_OPERATORS.get(
                type(node.op)
            )
        )

        if operator_function is None:
            raise ValueError(
                "Unsupported math operator."
            )

        left = _evaluate_math_node(
            node.left
        )

        right = _evaluate_math_node(
            node.right
        )

        if (
            isinstance(
                node.op,
                ast.Pow,
            )
            and abs(right)
            > MAX_ABS_EXPONENT
        ):
            raise ValueError(
                "Exponent is too large."
            )

        result = operator_function(
            left,
            right,
        )

        if abs(result) > MAX_ABS_RESULT:
            raise ValueError(
                "Calculation result is too large."
            )

        return result

    raise ValueError(
        "Unsupported expression."
    )


def normalize_math_expression(
    expression,
):
    return (
        expression
        .strip()
        .replace("×", "*")
        .replace("÷", "/")
        .replace("^", "**")
    )


def calculate(expression):
    normalized = normalize_math_expression(
        expression
    )

    if not normalized:
        raise ValueError(
            "No calculation was provided."
        )

    try:
        parsed = ast.parse(
            normalized,
            mode="eval",
        )

        result = _evaluate_math_node(
            parsed
        )

    except ZeroDivisionError:
        raise ValueError(
            "Division by zero is not allowed."
        )

    except SyntaxError:
        raise ValueError(
            "Invalid calculation."
        )

    if isinstance(result, float):
        if result.is_integer():
            return int(result)

        return round(
            result,
            10,
        )

    return result


def show_calculation_in_calculator(
    expression,
):
    """
    Safely calculate an arithmetic expression, launch Windows Calculator,
    and display the calculation/result inside the Calculator window.
    """

    normalized = normalize_math_expression(
        expression
    )

    result = calculate(
        normalized
    )

    launch_app(
        "calculator"
    )

    time.sleep(
        1.2
    )

    pyautogui.FAILSAFE = True

    try:
        calculator_windows = (
            pyautogui
            .getWindowsWithTitle(
                "Calculator"
            )
        )

        if calculator_windows:
            calculator_window = (
                calculator_windows[-1]
            )

            try:
                if calculator_window.isMinimized:
                    calculator_window.restore()
            except Exception:
                pass

            try:
                calculator_window.activate()

                time.sleep(
                    0.25
                )

            except Exception:
                pass

    except Exception:
        pass

    pyautogui.press(
        "esc"
    )

    keyboard_expression = (
        normalized
        .replace(" ", "")
    )

    simple_keyboard_expression = (
        "**" not in keyboard_expression
        and "//" not in keyboard_expression
        and "%" not in keyboard_expression
        and all(
            character
            in "0123456789+-*/()."
            for character
            in keyboard_expression
        )
    )

    if simple_keyboard_expression:
        pyautogui.write(
            keyboard_expression,
            interval=0.05,
        )

        pyautogui.press(
            "enter"
        )

    else:
        pyautogui.write(
            str(result),
            interval=0.05,
        )

    return (
        f"Launched calculator. "
        f"{normalized} = {result}. "
        f"The answer is displayed in Calculator."
    )


def make_keyboard_safe_text(text):
    """
    Convert common Unicode punctuation into characters that
    PyAutoGUI can type reliably with a normal Windows keyboard.
    """

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u2022": "-",
        "\u00a0": " ",
    }

    for source, replacement in replacements.items():
        text = text.replace(
            source,
            replacement,
        )

    # PyAutoGUI typing is most reliable with ordinary keyboard text.
    return (
        text
        .encode(
            "ascii",
            errors="replace",
        )
        .decode("ascii")
    )


def type_multiline_text(text):
    """
    Type plain text into the currently focused application while
    preserving paragraph breaks.
    """

    safe_text = make_keyboard_safe_text(
        text
    )

    safe_text = (
        safe_text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\t", "    ")
    )

    lines = safe_text.split(
        "\n"
    )

    for index, line in enumerate(
        lines
    ):
        if line:
            pyautogui.write(
                line,
                interval=0.01,
            )

        if index < len(lines) - 1:
            pyautogui.press(
                "enter"
            )


def open_notepad_and_type(text):
    """
    Launch approved Notepad and type plain text into it.

    This function does not execute the text, run shell commands,
    or save the document automatically.
    """

    text = str(
        text
    ).strip()

    if not text:
        raise ValueError(
            "No text was provided for Notepad."
        )

    if len(text) > MAX_NOTEPAD_TYPE_CHARS:
        raise ValueError(
            "The Notepad text is too long for "
            "the current typing limit."
        )

    launch_app(
        "notepad"
    )

    time.sleep(
        1.0
    )

    pyautogui.FAILSAFE = True

    try:
        windows = (
            pyautogui
            .getWindowsWithTitle(
                "Notepad"
            )
        )

        if windows:
            window = windows[-1]

            try:
                if window.isMinimized:
                    window.restore()
            except Exception:
                pass

            try:
                window.activate()

                time.sleep(
                    0.25
                )

            except Exception:
                pass

    except Exception:
        pass

    type_multiline_text(
        text
    )

    return (
        "Opened Notepad and typed the requested text."
    )


def extract_math_expression(text):
    pattern = re.compile(
        r"(?<![\w.])"
        r"-?\d+(?:\.\d+)?"
        r"(?:\s*(?:\*\*|[+\-*/%^×÷xX])\s*-?\d+(?:\.\d+)?)+"
        r"(?![\w.])"
    )

    match = pattern.search(
        text
    )

    if not match:
        return None

    expression = match.group(
        0
    )

    expression = re.sub(
        r"(?<=\d)\s*[xX]\s*(?=-?\d)",
        "*",
        expression,
    )

    return normalize_math_expression(
        expression
    )


if __name__ == "__main__":
    print(
        "EV PC Tools Test"
    )

    print(
        f"Time: {get_current_time()}"
    )

    print(
        f"Date: {get_current_date()}"
    )

    print(
        "Approved apps:"
    )

    for app in APP_ALLOWLIST:
        print(
            f"- {app}"
        )

    print(
        f"Calculator test: "
        f"2 + 2 = {calculate('2 + 2')}"
    )
