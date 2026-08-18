from pathlib import Path


# =====================================================
# EV v0.9 Safe File Creation
# =====================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

ALLOWED_FILE_EXTENSIONS = {
    ".txt",
    ".md",
}

MAX_FILENAME_CHARS = 120
MAX_FILE_WRITE_CHARS = 20000


def ensure_data_directory():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return DATA_DIR


def validate_safe_filename(filename):
    """
    Validate a simple filename.

    Nested directories, absolute paths, traversal, drive
    prefixes, and unsupported extensions are rejected.
    """

    if not isinstance(
        filename,
        str,
    ):
        raise ValueError(
            "Filename must be a string."
        )

    filename = filename.strip()

    if not filename:
        raise ValueError(
            "Filename cannot be empty."
        )

    if len(filename) > MAX_FILENAME_CHARS:
        raise ValueError(
            "Filename is too long."
        )

    path = Path(
        filename
    )

    if path.is_absolute():
        raise ValueError(
            "Absolute file paths are not allowed."
        )

    if path.name != filename:
        raise ValueError(
            "Nested file paths are not allowed."
        )

    if (
        "/" in filename
        or "\\" in filename
        or ":" in filename
        or filename in {
            ".",
            "..",
        }
    ):
        raise ValueError(
            "Only a simple filename is allowed."
        )

    extension = (
        path.suffix
        .lower()
    )

    if extension not in ALLOWED_FILE_EXTENSIONS:
        approved = ", ".join(
            sorted(
                ALLOWED_FILE_EXTENSIONS
            )
        )

        raise ValueError(
            f"File type '{extension or '(none)'}' "
            f"is not approved. "
            f"Approved types: {approved}"
        )

    return filename


def get_safe_write_path(filename):
    """
    Resolve a filename inside EV's approved data directory
    and verify that it cannot escape the directory.
    """

    safe_filename = validate_safe_filename(
        filename
    )

    data_root = (
        ensure_data_directory()
        .resolve()
    )

    target = (
        data_root
        / safe_filename
    ).resolve()

    try:
        target.relative_to(
            data_root
        )

    except ValueError as exc:
        raise ValueError(
            "File path escapes the approved data folder."
        ) from exc

    return target


def create_text_file(
    filename,
    content,
):
    """
    Create a NEW approved text/Markdown file.

    Existing files are never overwritten.
    """

    target = get_safe_write_path(
        filename
    )

    content = str(
        content
    )

    if len(content) > MAX_FILE_WRITE_CHARS:
        raise ValueError(
            "File content is too long for "
            "the current safe write limit."
        )

    try:
        with target.open(
            "x",
            encoding="utf-8",
            newline="",
        ) as file_handle:
            file_handle.write(
                content
            )

    except FileExistsError as exc:
        raise ValueError(
            f"File '{target.name}' already exists. "
            "EV will not overwrite existing files."
        ) from exc

    return (
        f"Created {target.name} in "
        "EV's approved data folder."
    )


def append_text_file(
    filename,
    content,
):
    """
    Append text to an EXISTING approved text/Markdown file.

    The existing file is preserved. EV never truncates or
    overwrites it through this function.
    """

    target = get_safe_write_path(
        filename
    )

    content = str(
        content
    )

    if len(content) > MAX_FILE_WRITE_CHARS:
        raise ValueError(
            "File content is too long for "
            "the current safe write limit."
        )

    if not target.exists():
        raise ValueError(
            f"File '{target.name}' does not exist. "
            "EV will not create it through append_file."
        )

    if not target.is_file():
        raise ValueError(
            f"'{target.name}' is not a regular file."
        )

    prefix = ""

    try:
        existing_size = target.stat().st_size

        if existing_size > 0:
            prefix = "\n"

    except OSError:
        pass

    with target.open(
        "a",
        encoding="utf-8",
        newline="",
    ) as file_handle:
        file_handle.write(
            prefix + content
        )

    return (
        f"Appended text to {target.name} in "
        "EV's approved data folder."
    )


if __name__ == "__main__":
    print(
        "EV v0.9 Safe File Creation"
    )

    print(
        "Approved extensions:"
    )

    for extension in sorted(
        ALLOWED_FILE_EXTENSIONS
    ):
        print(
            f"- {extension}"
        )
