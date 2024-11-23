from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from libs.mocks import MockSession

def transactional(func):
    @wraps(func)
    def wrapper(session, *args, **kwargs):
        if type(session) is MockSession:
            return func(session, *args, **kwargs)
        already_in_transaction = session.in_transaction()

        try:
            if not already_in_transaction:
                with session.begin():
                    return func(session, *args, **kwargs)
            else:
                return func(session, *args, **kwargs)

        except SQLAlchemyError as e:
            print(f"Error during transaction: {e}")
            if not already_in_transaction:
                session.rollback()
            raise

    return wrapper
