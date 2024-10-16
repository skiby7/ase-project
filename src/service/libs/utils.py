import re


def validate_user(first_name: str, last_name: str, email: str) -> bool:
    email_pattern = re.compile("^(?=.{1,64}@)[A-Za-z0-9_-]+(\\.[A-Za-z0-9_-]+)*@[^-][A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*(\\.[A-Za-z]{2,})$")
    return first_name.isalpha() and last_name.isalpha() and bool(email_pattern.match(email))
