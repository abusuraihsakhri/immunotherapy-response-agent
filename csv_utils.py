"""Shared CSV boolean parsing; never treat non-empty 'False' as true."""


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off", ""}:
        return False
    raise ValueError(f"Unrecognized boolean value: {value!r}")
