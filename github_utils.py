from github import Github, GithubException
import os
import base64
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# GitHub repository settings (can be overridden by environment variables)
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME") or "Azerus96"
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY") or "deeprofc"
AI_PROGRESS_FILENAME = "cfr_data.pkl"

def save_ai_progress_to_github(filename=AI_PROGRESS_FILENAME):
    token = os.environ.get("AI_PROGRESS_TOKEN")
    if not token:
        logger.warning("AI_PROGRESS_TOKEN not set. Progress saving to GitHub disabled.")
        return False

    try:
        g = Github(token)
        repo = g.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPOSITORY)

        try:
            contents = repo.get_contents(filename, ref="main")
            # Используем 'with' для автоматического закрытия файла
            with open(filename, 'rb') as f:
                content = f.read()
            # Нет необходимости в .decode('utf-8') после base64.b64encode()
            repo.update_file(contents.path, "Update AI progress", base64.b64encode(content), contents.sha, branch="main")
            logger.info(f"AI progress saved to GitHub: {GITHUB_REPOSITORY}/{filename}")
            return True
        except GithubException as e:
            if e.status == 404:
                # Используем 'with' для автоматического закрытия файла
                with open(filename, 'rb') as f:
                    content = f.read()
                # Нет необходимости в .decode('utf-8') после base64.b64encode()
                repo.create_file(filename, "Initial AI progress", base64.b64encode(content), branch="main")
                logger.info(f"Created new file for AI progress on GitHub: {GITHUB_REPOSITORY}/{filename}")
                return True
            else:
                logger.error(f"Error saving progress to GitHub (other than 404): {e}")
                return False

    except GithubException as e:
        logger.error(f"Error saving progress to GitHub: {e}")
        return False
    except Exception as e:
        logger.exception(f"An unexpected error occurred during saving: {e}")
        return False


def load_ai_progress_from_github(filename=AI_PROGRESS_FILENAME):
    token = os.environ.get("AI_PROGRESS_TOKEN")
    if not token:
        logger.warning("AI_PROGRESS_TOKEN not set. Progress loading from GitHub disabled.")
        return False

    try:
        g = Github(token)
        repo = g.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPOSITORY)
        contents = repo.get_contents(filename, ref="main")
        file_content = base64.b64decode(contents.content)
        # Используем 'with' для автоматического закрытия файла
        with open(filename, 'wb') as f:
            f.write(file_content)
        logger.info(f"AI progress loaded from GitHub: {GITHUB_REPOSITORY}/{filename}")
        return True

    except GithubException as e:
        if e.status == 404:
            logger.info("Progress file not found in GitHub repository.")
            return False
        else:
            logger.error(f"Error loading progress from GitHub: {e}")
            return False
    except Exception as e:
        logger.exception(f"An unexpected error occurred during loading: {e}")
        return False
