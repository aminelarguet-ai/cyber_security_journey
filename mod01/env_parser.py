import os
from abc import ABC, abstractmethod
import tempfile


class Pathchecker:
    def __init__(self, file_path):
        self.file_path = file_path

    def check(self):
        return os.path.exists(self.file_path)


class CleanFile:
    def __init__(self, file_path, checker):
        self.file_path = file_path
        self.checker = checker
        self.dir_name = os.path.dirname(self.file_path)

    def clean(self):
        text = []
        if not self.checker.check():
            raise FileNotFoundError(f"file {self.file_path} not found")

        with open(self.file_path, "r") as f, tempfile.NamedTemporaryFile(
            mode="w",
            dir=self.dir_name,
            delete=False
        ) as tmp:

            temp_path = tmp.name

            content = f.read()

            if not content:
                raise ValueError(f"file '{self.file_path}' is empty")

            for line in content.splitlines():
                line = line.strip()

                if not line:

                    continue

                tmp.write(line + "\n")
                text.append(line)

        os.replace(temp_path, self.file_path)
        return text


class Converter:

    def _is_int(self, value):
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    def _is_float(self, value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def convert(self, value):
        if value is None or value == "":
            return ""

        if isinstance(value, str):
            lower = value.lower()

            if lower == "true":
                return True

            elif lower == "false":
                return False

            elif (
                (value.startswith("'") and value.endswith("'")) or
                (value.startswith('"') and value.endswith('"'))
            ):
                return value[1:-1]

        if self._is_int(value):
            return int(value)

        if self._is_float(value):
            return float(value)

        return value


class Parser:
    def __init__(self):
        self.data = {}
        self.comments = {}
        self.converter = Converter()

    def _inside_comment(self, string):
        # cheking the presence if comments in the value strings and returning them f found
        value = ""
        comment = ""
        in_quote = False
        idx = None
        for i, char in enumerate(string):

            if char in ("'", '"') and in_quote == False:

                in_quote = True
            else:
                if char in ("'", '"') and in_quote == True:
                    in_quote = False

            if char == "#" and not in_quote:
                idx = i
                value = string[:idx]
                comment = string[idx+1:]
                break
        if idx is not None:
            value = string[:idx]
            comment = string[idx+1:]
        else:
            value = string
            comment = ""

        return value, comment

    def _expand(self):

        if not self.data:
            return None

        for key in list(self.data.keys()):
            value = str(self.data[key])

            seen_states = set()

            while "${" in value:
                if value in seen_states:
                    print(
                        f"Circular reference detected while expanding '{key}'")
                    break

                seen_states.add(value)

                start = value.find("${")
                end = value.find("}", start)

                if end == -1:
                    break

                var = value[start + 2:end]

                replacement = str(self.data.get(var, f"${{{var}}}"))

                value = value[:start] + replacement + value[end + 1:]

            self.data[key] = self.converter.convert(value)
        return self.data

    def parse(self, text):
        for idx, line in enumerate(text):
            if line.startswith("#"):
                self.comments[f"line {idx+1}"] = line
            else:
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value, nested_comment = self._inside_comment(value)
                    value = self.converter.convert(value)
                    if value == "":
                        self.data[key] = f"missing value by line {idx+1}"
                    else:
                        self.data[key] = value

                    if nested_comment:
                        self.comments[f"extracted comment {idx+1}"] = nested_comment
        self._expand()


class EnvStore:
    SENSITIVE = {"password", "secret", "key", "token", "api"}

    def __init__(self):
        self._store = {}

    def load(self, data):
        for key, value in data.items():
            self._store[key] = str(value)

    def get(self, key, default=None, masked=False):
        value = self._store.get(key, default)
        if self._is_sensitive(key) or masked:
            return self._mask(str(value))
        return value

    def require(self, key_list):
        catched_error = {}

        for key in key_list:
            if key not in self._store:
                catched_error[key] = f"missing required key: {key}"

        if catched_error:
            for msg in catched_error.values():

                print(f"{msg}")
            raise ValueError(
                f"Missing required keys: {list(catched_error.keys())}")
        print("all keys have been successfully tested")

    def _mask(self, string):
        if len(string) <= 4:
            return "*" * len(string)
        return string[:4] + "*" * (len(string)-4)

    def _is_sensitive(self, key):
        # find common values that wwe want to be masked while treating few edge cases such as monkey
        parts = key.lower().split("_")
        return any(part in self.SENSITIVE for part in parts)


class EnvFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def exists(self):
        if os.path.exists(self.file_path):
            return True
        else:
            return False

    def _format(self, data):
        return [f"{key}={value}\n" for key, value in data.items()]

    def write(self, data, overwrite=False):
        if not data:
            return None
        if self.exists() and not overwrite:
            print(f"this file {self.file_path} already exists")
            return None

        lines = self._format(data)

        with open(self.file_path, "w") as f:
            f.writelines(lines)

        return True


class BaseStore(ABC):          # inherit from ABC to enable abstract methods

    @abstractmethod
    def get(self, key, default=None):
        pass

    @abstractmethod
    def require(self, key_list):
        pass

if __name__ == "__main__":
    pass 