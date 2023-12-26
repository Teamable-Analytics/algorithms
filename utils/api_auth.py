import os
from bcrypt import hashpw, gensalt, checkpw

from pathlib import Path
import dotenv
env_file = next((Path(__file__).parent.parent / "env").glob("*.env"))
dotenv.load_dotenv(dotenv_path=env_file)


def encrypt_api_auth_token(api_token):
    """
    Encrypts the API token using bcrypt.

    This function only serves to encrypt a new API token for customers and should never get called in production.
    """
    return hashpw(
        password=api_token.encode("utf-8"),
        salt=gensalt(),
    )


def check_hash(api_token, encrypted_api_token):
    return checkpw(
        password=api_token.encode("utf-8"),
        hashed_password=encrypted_api_token.encode("utf-8"),
    )


def is_api_key_valid(api_key):
    """
    Validates the API key by checking if it is in the database.
    """
    allowed_api_keys = os.getenv("API_AUTH_ALLOWED_KEYS").split(" ")
    return any(check_hash(api_key, allowed_api_key) for allowed_api_key in allowed_api_keys)
