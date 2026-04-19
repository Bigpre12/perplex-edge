"""Load .env from predictable locations so the API works regardless of cwd."""
import os

from dotenv import load_dotenv


def load_project_dotenv() -> None:
    _here = os.path.dirname(os.path.abspath(__file__))
    api_root = os.path.abspath(os.path.join(_here, "..", ".."))
    repo_root = os.path.abspath(os.path.join(_here, "..", "..", "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))
    load_dotenv(os.path.join(api_root, ".env"))
    load_dotenv(os.path.join(os.getcwd(), ".env"), override=True)
