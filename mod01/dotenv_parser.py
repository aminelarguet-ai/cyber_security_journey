import os
from dotenv import dotenv_values, set_key


# --- Converter utilities ---

def _is_int(value):
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def _is_float(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def convert(value):
    if value is None or value == "":
        return ""

    if isinstance(value, str):

        lower = value.lower()

        if lower == "true":
            return True

        elif lower == "false":
            return False

        elif (
            (value.startswith("'") and value.endswith("'"))
            or
            (value.startswith('"') and value.endswith('"'))
        ):
            return value[1:-1]

    if _is_int(value):
        return int(value)

    if _is_float(value):
        return float(value)

    return value


# --- Core parser using dotenv ---

def read_and_parse(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"file {file_path} not found"
        )

    data = {}
    comments = {}

    values = dotenv_values(
        file_path,
        interpolate=False
    )


    with open(file_path, "r") as f:
        lines = f.readlines()


    line_map = {}

    for index, line in enumerate(lines, start=1):

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            comments[f"line {index}"] = stripped
            continue


        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            line_map[key] = index


            # preserve inline comments
            value = stripped.split("=", 1)[1]

            in_quote = False

            for i, char in enumerate(value):

                if char in ("'", '"'):
                    in_quote = not in_quote

                elif char == "#" and not in_quote:
                    comments[
                        f"extracted comment {index}"
                    ] = value[i + 1:].strip()
                    break


    for key, value in values.items():

        line = line_map.get(key, "?")

        converted = convert(value)

        if converted == "":
            data[key] = (
                f"missing value by line {line}"
            )

        else:
            data[key] = converted


    data = expand(data)

    return data, comments



# --- Variable expansion ---

def expand(data):

    if not data:
        return {}

    result = dict(data)


    for key in list(result.keys()):

        value = str(result[key])

        seen_states = set()


        while "${" in value:

            if value in seen_states:
                break


            seen_states.add(value)


            start = value.find("${")
            end = value.find("}", start)


            if end == -1:
                break


            var = value[start + 2:end]


            replacement = str(
                result.get(
                    var,
                    f"${{{var}}}"
                )
            )


            value = (
                value[:start]
                +
                replacement
                +
                value[end + 1:]
            )


        result[key] = convert(value)


    return result



# --- Security utilities ---

SENSITIVE = {
    "password",
    "secret",
    "key",
    "token",
    "api"
}


def is_sensitive(key):

    parts = key.lower().split("_")

    return any(
        part in SENSITIVE
        for part in parts
    )



def mask(string):

    if len(string) <= 4:
        return "*" * len(string)

    return string[:4] + "*" * (len(string)-4)

def to_safe_log(data: dict) -> dict:
    """
    Return a copy of data safe for logging.
    Sensitive keys have their values masked.
    Non-sensitive keys remain unchanged.
    """

    safe_data = {}

    for key, value in data.items():
        if is_sensitive(key):
            safe_data[key] = mask(str(value))
        else:
            safe_data[key] = value

    return safe_data


# --- Environment writer using dotenv ---

def write_env(
    file_path,
    data,
    overwrite=False
):

    if not data:
        return None


    if os.path.exists(file_path) and not overwrite:
        return None


    directory = os.path.dirname(file_path)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )


    if not os.path.exists(file_path):

        open(
            file_path,
            "w"
        ).close()


    for key, value in data.items():

        set_key(
            file_path,
            key,
            str(value),
            quote_mode="never"
        )


    return True

