# InstantGitSearch

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg)
![GitHub API](https://img.shields.io/badge/GitHub-REST%20API-181717.svg)

A lightweight Python command-line project for exploring GitHub user data through the GitHub REST API. It is designed as a simple interactive utility to practice working with API requests, environment variables, and authenticated GitHub actions.

## Overview

InstantGitSearch lets you:

- Search for a GitHub user by username
- View profile details such as name, follower count, following count, and repository count
- Inspect a user’s public repositories and star counts
- Follow or unfollow a user through authenticated API requests
- Navigate the tool through a simple terminal menu

This project is intentionally minimal and beginner-friendly, making it a good example of how to build a small CLI around a REST API.

## Features

- GitHub user lookup by exact username
- Interactive terminal interface
- Repository listing and summary output
- Follow/unfollow operations via authenticated requests
- Environment-based GitHub token configuration
- Easy local installation with Python packaging

## Tech Stack

- Python 3.12+
- requests
- python-dotenv
- GitHub REST API

## Project Structure

- `fgit.py` — main CLI application logic
- `pyproject.toml` — package metadata, dependencies, and CLI entry point
- `test_fgit.py` — automated tests for the API and CLI behavior
- `AUTH_KEYS.env` — local environment file for the GitHub PAT
- `REQ_KEYS.env.example` — configuration template
- `README.md` — project documentation

## Prerequisites

Before running the project, ensure you have:

- Python 3.12 or newer
- A GitHub account
- A GitHub Personal Access Token (PAT) with the permissions required for the actions you plan to use
- `pip` for installing Python dependencies

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd instantgitsearch
```

### 2. Configure your environment

Create a file named `AUTH_KEYS.env` in the project root and add your token:

```bash
GITHUB_PAT=your_github_personal_access_token_here
```

> The script reads the value from `GITHUB_PAT` in `AUTH_KEYS.env`.

### 3. Install dependencies

Create and activate a virtual environment, then install the project and its test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Run the application

```bash
instantgitsearch
```

You can also run the application directly with `python fgit.py`.

## Tests

Run the test suite from the project root with:

```bash
python -m pytest -v
```

Running the tests is recommended after making changes to check that API requests and menu behavior still work as expected.

## Usage

When the app starts, it prompts for a GitHub username and then displays a menu similar to:

```text
Enter username: octocat

Welcome:
1. profile octocat
2. follow octocat
3. unfollow octocat
4. see repositories
5. exit
```

Available actions:

1. View profile
2. Follow user
3. Unfollow user
4. See repositories
5. Exit

## Example Output

```text
************octocat Info*****************
name = The Octocat
followers = 12345
following = 14
repository num = 9
```

## Notes

- This project is intended for learning and experimentation rather than production-grade automation.
- GitHub API rate limits may apply depending on the token type and usage patterns.
- Follow and unfollow operations require authentication and will be subject to GitHub’s API rules.
- Request errors during a menu action are reported to standard error; the menu remains available afterward.

## License

This project is provided for educational purposes and does not currently include a formal license file.

