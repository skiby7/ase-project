from functools import wraps
from logging import getLogger

logger = getLogger("uvicorn.error")

def transactional(func):
    @wraps(func)
    def wrapper(session, *args, **kwargs):
        already_in_transaction = session.in_transaction()

        try:
            if not already_in_transaction:
                with session.begin():
                    return func(session, *args, **kwargs)
            else:
                return func(session, *args, **kwargs)

        except Exception as e:
            logger.error(f"Error during transaction: {e}")
            if not already_in_transaction:
                logger.info("Rolling back transaction...")
                session.rollback()
            raise

    return wrapper
