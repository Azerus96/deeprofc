from github import Github, GithubException
import os
import base64
import logging
from typing import Optional

# Настройка логирования
logger = logging.getLogger(__name__)

# GitHub repository settings (can be overridden by environment variables)
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME") or "Azerus96"
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY") or "deeprofc"
AI_PROGRESS_FILENAME = "cfr_data.pkl"


def save_ai_progress_to_github(filename: str = AI_PROGRESS_FILENAME) -> bool:
    """
    Saves AI progress file to GitHub repository.

    Args:
        filename (str): Name of the file to save. Defaults to AI_PROGRESS_FILENAME.

    Returns:
        bool: True if save was successful, False otherwise.
    """
    token = os.environ.get("AI_PROGRESS_TOKEN")
    if not token:
        logger.warning("AI_PROGRESS_TOKEN not set. Progress saving to GitHub disabled.")
        return False

    # Проверка существования локального файла
    if not os.path.exists(filename):
        logger.error(f"Local file {filename} does not exist. Cannot save to GitHub.")
        return False

    try:
        g = Github(token)
        repo = g.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPOSITORY)

        try:
            contents = repo.get_contents(filename, ref="main")
            with open(filename, "rb") as f:
                content = f.read()
            repo.update_file(
                contents.path,
                "Update AI progress",
                base64.b64encode(content),
                contents.sha,
                branch="main",
            )
            logger.info(f"AI progress updated on GitHub: {GITHUB_REPOSITORY}/{filename}")
            return True
        except GithubException as e:
            if e.status == 404:
                with open(filename, "rb") as f:
                    content = f.read()
                repo.create_file(
                    filename,
                    "Initial AI progress",
                    base64.b64encode(content),
                    branch="main",
                )
                logger.info(f"Created new file for AI progress on GitHub: {GITHUB_REPOSITORY}/{filename}")
                return True
            else:
                logger.error(f"GitHub API error saving progress: status={e.status}, data={e.data}")
                return False

    except GithubException as e:
        logger.error(f"GitHub API error saving progress: status={e.status}, data={e.data}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during saving to GitHub: {e}")
        return False


def load_ai_progress_from_github(filename: str = AI_PROGRESS_FILENAME) -> bool:
    """
    Loads AI progress file from GitHub repository.

    Args:
        filename (str): Name of the file to load. Defaults to AI_PROGRESS_FILENAME.

    Returns:
        bool: True if load was successful, False otherwise.
    """
    token = os.environ.get("AI_PROGRESS_TOKEN")
    if not token:
        logger.warning("AI_PROGRESS_TOKEN not set. Progress loading from GitHub disabled.")
        return False

    try:
        g = Github(token)
        repo = g.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPOSITORY)
        contents = repo.get_contents(filename, ref="main")
        file_content = base64.b64decode(contents.content)
        with open(filename, "wb") as f:
            f.write(file_content)
        logger.info(f"AI progress loaded from GitHub: {GITHUB_REPOSITORY}/{filename}")
        return True

    except GithubException as e:
        if e.status == 404:
            logger.info(f"Progress file {filename} not found in GitHub repository.")
            return False
        else:
            logger.error(f"GitHub API error loading progress: status={e.status}, data={e.data}")
            return False
    except Exception as e:
        logger.exception(f"Unexpected error during loading from GitHub: {e}")
        return False
