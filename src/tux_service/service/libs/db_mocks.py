import os

def use_mocks(func):
    def wrapper(*args, **kwargs):
        if os.getenv("TEST_RUN", "false").lower() == "true":
            mock_func = getattr(f"{func.__name__}_mock", locals()[__name__], default_mock)
            print(f"Function {func.__name__} is mocked.")
            return mock_func(*args, **kwargs)
        print(f"Function {func.__name__} is executed normally.")
        return func(*args, **kwargs)
    return wrapper

def default_mock(*args, **kwargs):
    pass
