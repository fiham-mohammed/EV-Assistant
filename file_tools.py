from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
}


def ensure_data_directory():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def list_files():
    ensure_data_directory()

    files = []

    for path in DATA_DIR.iterdir():
        if (
            path.is_file()
            and path.suffix.lower() in ALLOWED_EXTENSIONS
        ):
            files.append(path.name)

    return sorted(files)


def get_safe_path(filename):
    ensure_data_directory()

    requested_path = (
        DATA_DIR / filename
    ).resolve()

    data_root = DATA_DIR.resolve()

    try:
        requested_path.relative_to(
            data_root
        )
    except ValueError:
        raise ValueError(
            "Access denied: file must be inside the data folder."
        )

    return requested_path


def read_file(filename):
    path = get_safe_path(
        filename
    )

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {filename}"
        )

    if not path.is_file():
        raise ValueError(
            "Requested path is not a file."
        )

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type."
        )

    return path.read_text(
        encoding="utf-8"
    )


if __name__ == "__main__":
    print(
        "Approved EV files:"
    )

    for file_name in list_files():
        print(
            f"- {file_name}"
        )