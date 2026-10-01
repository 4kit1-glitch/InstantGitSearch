"""Auto do a limited amount of research on a GitHub user."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - handles environments without the package installed
    def load_dotenv(*_args, **_kwargs):
        """Fallback loader used when python-dotenv is unavailable."""
        return False


BASE_DIR = Path(__file__).resolve().parent
_ENV_PATH = BASE_DIR / "AUTH_KEYS.env"


def get_env() -> str:
    """Load and return the GitHub token from the local environment file."""
    load_dotenv(_ENV_PATH)

    value = os.environ.get("GITHUB_PAT")
    if value is None or not value.strip():
        raise SystemExit("PAT token not found. Please add GITHUB_PAT to AUTH_KEYS.env")
    return value


AUTH_TOKEN = get_env()
BASE_URL = "https://api.github.com"
TIME_OUT = 10

BASE_HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}


def _pause() -> None:
    """Pause the script and clear the terminal output."""
    print("press enter to continue..", end="")
    input()
    subprocess.run("cls" if os.name == "nt" else "clear", check=False)


def perform_request(url: str, header: dict[str, str], time: int = 10) -> Any:
    """Perform a GET request to the provided GitHub API URL."""
    try:
        response = requests.get(
            url,
            headers=header,
            timeout=time,
            params={"per_page": 100, "page": 1},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"Error occurred: {err}")
        raise


def get_user(user_name: str) -> dict | None:
    """Fetch a GitHub user profile by username."""
    user_url = f"{BASE_URL}/users/{user_name}"

    data = perform_request(user_url, BASE_HEADERS, TIME_OUT)
    try:
        output = {
            "login": data["login"],
            "followers": data["followers"],
            "following": data["following"],
            "repo_count": data["public_repos"],
            "following_url": data["following_url"],
            "followers_url": data["followers_url"],
            "repo_url": data["repos_url"],
            "name": data.get("name", "not specified"),
        }
        return output
    except (KeyError, TypeError, ValueError) as err:
        print(f"Value error: {err}")
        raise


def profile_user(info: dict) -> None:
    """Print a formatted summary of a user profile."""
    name = info.get("name", "unspecified")
    uname = info.get("login", "unspecified")
    repo_count = info.get("repo_count")
    follower_count = info.get("followers")
    following_count = info.get("following")
    print(
        f"""
************{uname} Info*****************
name = {name}
followers = {follower_count}
following = {following_count}
repository num = {repo_count}
"""
    )


def follow(user_name: str) -> None:
    """Follow a user on GitHub."""
    follow_url = f"{BASE_URL}/user/following/{user_name}"
    try:
        response = requests.put(follow_url, headers=BASE_HEADERS, timeout=TIME_OUT)
        if response.status_code == 422:
            print("Can't follow yourself")
            return
    except requests.RequestException as err:
        print(f"ERROR OCCURRED: {err}")
        return

    response.raise_for_status()
    print(f"Followed {user_name}")


def unfollow(user_name: str) -> None:
    """Unfollow a user on GitHub."""
    follow_url = f"{BASE_URL}/user/following/{user_name}"
    try:
        response = requests.delete(follow_url, headers=BASE_HEADERS, timeout=TIME_OUT)
        if response.status_code == 422:
            print("Can't unfollow yourself")
            return
    except requests.RequestException as err:
        print(f"ERROR OCCURRED: {err}")
        return

    response.raise_for_status()
    print(f"Unfollowed {user_name}")


def see_repos(user_name: str) -> None:
    """Print a simple list of a user's repositories and star counts."""
    repo_url = f"{BASE_URL}/users/{user_name}/repos"
    try:
        response = requests.get(repo_url, headers=BASE_HEADERS, timeout=TIME_OUT)
        response.raise_for_status()
        repos = response.json()

        if not repos:
            print("No public repositories found.")
            return

        print(f"{'name':<40} {'stars':>6}")
        for repo in repos:
            print(f"{repo['name']:<40} {repo['stargazers_count']:>6}")
    except (ValueError, requests.RequestException) as err:
        print(f"Error occurred: {err}")


def front_end(name: str) -> None:
    """Display the interactive repository menu."""
    print(
        f"""
Welcome:
1. profile {name}
2. follow {name}
3. unfollow {name}
4. see repositories
5. exit

"""
    )


def handle_option(option: int, data: dict) -> bool:
    """Execute the selected menu item and return whether the app should exit."""
    login = data["login"]

    if option == 1:
        profile_user(data)
        return False
    if option == 2:
        follow(login)
        return False
    if option == 3:
        unfollow(login)
        return False
    if option == 4:
        see_repos(login)
        return False
    if option == 5:
        print("Exiting...")
        return True

    print(f"Unknown input {option}, retry..")
    return False


def main() -> int:
    """Run the GitHub profile CLI."""
    user_name = input("Enter username: ")
    try:
        data = get_user(user_name)
    except requests.RequestException:
        print(f"Failed to get user {user_name}")
        return 1

    if not data:
        print("Could not load user data")
        return 1

    while True:
        front_end(data["name"])

        try:
            response = int(input("Select option: "))
        except ValueError:
            print("Please enter a number.")
            continue
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return 0

        try:
            should_exit = handle_option(response, data)
            if should_exit:
                return 0
            _pause()
        except (KeyboardInterrupt, ValueError) as err:
            print(f"Error occurred: {err}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
