from service.libs.utils import validate_user

def test_validate_user_valid():
    assert validate_user("Mario", "Rossi", "mariorossi@gmail.com")

def test_validate_user_invalid_email():
    assert not validate_user("Mario", "Rossi", "mariorossigmail.com")
    assert not validate_user("Mario", "Rossi", "mariorossi@gmail")
    assert not validate_user("Mario", "Rossi", "mariorossi@.com")

def test_validate_user_invalid_name():
    assert not validate_user("Mari.o", "Rossi", "mariorossi@gmail.com")
    assert not validate_user("Mario", "Ro55i", "mariorossi@gmail.com")
