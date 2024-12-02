import time
import requests
from ..utils.logger import logger

def retry_delete_operation(url: str, uid: str, access_token: str, max_retry=5, attempt=1):
    try:
        response = requests.delete(f"{url}/{uid}", headers= {"Authorization": f"Bearer {access_token}"}, timeout=5, verify=False)
        if response.status_code in [200, 404]:
            logger.info(f"Retry success: Notified {url} for deletion user {uid} on attempt {attempt}")
            return
        else:
            logger.error(f"Retry failed: {url} returned {response.status_code} on attempt {attempt}")
    except (requests.RequestException, ConnectionError):
        logger.error(f"Delete retry exception: {url}/{uid} - {e} on attempt {attempt}")
    if attempt >= max_retry:
        logger.error(f"Exceeded retry attempts for {url}/{uid}. Compensation needed.")
        return

    time.sleep(2**attempt)
    retry_delete_operation(url, uid, access_token, attempt=attempt + 1)

def retry_create_operation(url: str, account_dict: dict, access_token: str, max_retry=5, attempt=1):
    try:
        response = requests.post(url, headers= {"Authorization": f"Bearer {access_token}"},json=account_dict, timeout=5, verify=False)
        if response.status_code == 200:
            logger.info(f"Create retry success: notified {url} for creation user {account_dict} on attempt {attempt}")
            return
        else:
            logger.error(f"Create retry failed: {url} on attempt {attempt}")
    except (requests.RequestException, ConnectionError):
        logger.error(f"Create retry failed: {url} on attempt {attempt}")
    if attempt >= max_retry:
        logger.error(f"Exceeded create retry attempts for {url} for user {account_dict}. Compensation needed.")
        return

    time.sleep(2**attempt)
    retry_create_operation(url, account_dict, access_token, attempt=attempt + 1)
