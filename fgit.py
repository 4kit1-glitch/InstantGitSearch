"""
 Auto do a limited amount of research on a github user
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
_ENV_PATH = BASE_DIR / "AUTH_KEYS.env"


def get_env() -> str:
    """Load and return the GitHub personal access token."""
    load_dotenv(_ENV_PATH)

    value = os.environ.get("GITHUB_PAT")

    if value is None:
        raise SystemExit("PAT tocken not found pls add to AUTH_KEYS.env")
    return value

AUTH_TOKEN = get_env()
BASE_URL = "https://api.github.com"
TIME_OUT = 10 # ten seconds sever timeout

BASE_HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10"
}

def _pause() -> None:
    """Wait for the user to continue, then clear the terminal."""
    print("press enter to continue..", end="")
    input()
    subprocess.run('cls' if os.name == "nt" else 'clear', check=False)
    

def perform_request(url, header, time :int = 10) -> Any:
    """Send a paginated GET request and return its decoded JSON response."""
    try:
        response = requests.get(url, headers=header, timeout=time, params={"per_page": 100, "page": 1})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"Error occured: {err}")
        raise

def get_user(user_name: str) -> dict | None:
    """Fetch a GitHub user's profile details."""
    USER_URL = f"{BASE_URL}/users/{user_name}"

    data = perform_request(USER_URL, BASE_HEADERS, TIME_OUT)
    try:
        output = {
            "login": data["login"], "followers": data["followers"], 
            "following": data["following"], "repo_count": data["public_repos"],
            "following_url": data["following_url"], "followers_url": data["followers_url"],
            "repo_url": data["repos_url"], "name": data.get("name", "not specified")
        }
        return output
    except (ValueError, KeyError) as err:
        print(f"Value error: {err}")
        raise

def profile_user(info: dict) -> None:
    """Print the selected profile information."""
    name = info.get("name", "unspecified")
    uname = info.get("login", "unspecified")
    rcount = info.get("repo_count")
    follower_count = info.get("followers")
    following_count = info.get("following") 
    print(
f"""
************{uname} Info*****************
name = {name}
followers = {follower_count}
following = {following_count}
repository num = {rcount}
"""
)

def follow(user_name: str) -> None:
    """Follow a GitHub user using the configured account."""
    FOLLOW_URL = f"https://api.github.com/user/following/{user_name}"
    try:
        response = requests.put(FOLLOW_URL, headers=BASE_HEADERS, timeout=TIME_OUT)
        if response.status_code == 422:
            print("Cant follow your self")
            return
    except requests.RequestException as e:
        print(f"ERROR OCCURED: {e}")
        return

    response.raise_for_status()
    print(f"Followed {user_name}")
  

def unfollow(user_name: str) -> None:
    """Unfollow a GitHub user using the configured account."""
    FOLLOW_URL = f"https://api.github.com/user/following/{user_name}"
    try:
        response = requests.delete(FOLLOW_URL, headers=BASE_HEADERS, timeout=TIME_OUT)
        if response.status_code == 422:
            print("Cant unfollow your self")
            return 

    except requests.RequestException as e:
        print(f"ERROR OCCURED: {e}")
        return 

    response.raise_for_status()
    print(f"Unfollowed {user_name}")


def see_repos(user_name : str) -> None:
    """Print the user's public repositories and their star counts."""
    REPO_URL = f"{BASE_URL}/users/{user_name}/repos"
    response = requests.get(REPO_URL, headers=BASE_HEADERS, timeout=TIME_OUT)
    response.raise_for_status()
    repos = response.json()
    print(f"{"name"}{"stars".rjust(100)}")
    for repo in repos:
        print(f"{repo["name"]:<100} {repo["stargazers_count"]}")



def front_end(name: str) -> None:
    """Display the available actions for the selected user."""
    print(f"""
Welcome:
1. profile {name}
2. follow {name}
3. unfollow {name}
4. see repositories
5. exit

""")
    
def main() -> int:
    """Run the interactive GitHub user lookup and action menu."""
    user_name = input("Enter username: ")
    try:
        data = get_user(user_name)
        
    except requests.RequestException:
        print(f"failed to get user {user_name}")
        return 1

    if not data:
        print("could not load user data")
        return 1
    
    login = data["login"]

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
            match response:
                case 1:
                    profile_user(data)
                case 2:
                    follow(login)
                case 3:
                    unfollow(login)
                case 4:
                    see_repos(login)
                case 5:
                    print("exiting...")
                    return 0
                case _:
                    print(f"unknown input {response}, retry..")
            _pause()
        except requests.RequestException as err:
            print(f"Request failed: {err}", file=sys.stderr)
        except ValueError as err:
            print(f"error occured {err}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("Exiting..")
            return 0


if __name__ == "__main__":
    sys.exit(main())