import re

def validate_user(first_name: str, last_name: str, email: str) -> bool:
	first_name_pattern = re.compile("[a-zA-ZÀ-ÿ]+([ '-][a-zA-Z]+)*")
	last_name_pattern = re.compile("([a-zA-ZÀ-ÿ][-,a-z. 'À-ÿ]+[ ]*)+")
	email_pattern = re.compile("^(?=.{1,64}@)[A-Za-z0-9_-]+(\\.[A-Za-z0-9_-]+)*@[^-][A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*(\\.[A-Za-z]{2,})$")
	return bool(first_name_pattern.match(first_name)) and bool(last_name_pattern.match(last_name)) and (bool(email_pattern.match(email)) or bool(first_name_pattern.match(email)))
