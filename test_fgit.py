import pytest
from unittest.mock import Mock, call, patch
from requests.exceptions import HTTPError, RequestException

from fgit import (
    get_env, perform_request, get_user, follow, unfollow, see_repos,
    BASE_URL, BASE_HEADERS, TIME_OUT,
)



@patch("fgit.os.environ.get")
def test_get_env_returns_value(mock_get):
    mock_get.return_value = "myenvstr"
    assert get_env() == "myenvstr"


@patch("fgit.os.environ.get")
def test_get_env_raises_when_missing(mock_get):
    mock_get.return_value = None
    with pytest.raises(SystemExit):
        get_env()



@patch("fgit.requests.get")
def test_perform_request_returns_json(mock_get):
    mock_get.return_value.json.return_value = {"name": "john doe"}
    mock_get.return_value.raise_for_status.return_value = None

    result = perform_request(f"{BASE_URL}", {"header": "1"})

    assert result == {"name": "john doe"}


@patch("fgit.requests.get")
def test_perform_request_raises_on_http_error(mock_get):
    mock_get.return_value.raise_for_status.side_effect = HTTPError("404")

    with pytest.raises(HTTPError):
        perform_request(f"{BASE_URL}", {"header": "1"})


@patch("fgit.requests.get")
def test_perform_request_raises_on_connection_error(mock_get):
    mock_get.side_effect = RequestException("no internet")

    with pytest.raises(RequestException):
        perform_request(f"{BASE_URL}", {"header": "1"})



@patch("fgit.requests.get")
def test_get_user_returns_expected_fields(mock_get):
    mock_get.return_value.json.return_value = {
        "login": "octocat",
        "followers": 1,
        "following": 2,
        "public_repos": 3,
        "repos_url": f"{BASE_URL}/users/octocat/repos",
        "name": "Octocat",
    }
    mock_get.return_value.raise_for_status.return_value = None

    result = get_user("octocat") or {}

    assert result["login"] == "octocat"
    assert result["repo_count"] == 3
    assert result["name"] == "Octocat"


@patch("fgit.requests.get")
def test_get_user_calls_correct_url(mock_get):
    mock_get.return_value.json.return_value = {
        "login": "octocat", "followers": 0, "following": 0,
        "public_repos": 0, "repos_url": "x", "name": "x",
    }
    mock_get.return_value.raise_for_status.return_value = None

    get_user("octocat")

    mock_get.assert_called_once_with(
        f"{BASE_URL}/users/octocat",
        headers=BASE_HEADERS,
        timeout=TIME_OUT,
        params={"per_page": 100, "page": 1},
    )



@patch("fgit.requests.put")
def test_follow_calls_correct_url(mock_put):
    mock_put.return_value.raise_for_status.return_value = None

    follow("octocat")

    mock_put.assert_called_once_with(
        f"{BASE_URL}/user/following/octocat",
        headers=BASE_HEADERS,
        timeout=TIME_OUT,
    )


@patch("fgit.requests.put")
def test_follow_returns_early_for_422(mock_put):
    mock_put.return_value.status_code = 422

    follow("octocat")

    # raise_for_status should NOT be called when 422
    mock_put.return_value.raise_for_status.assert_not_called()



@patch("fgit.requests.delete")
def test_unfollow_calls_correct_url(mock_delete):
    mock_delete.return_value.raise_for_status.return_value = None

    unfollow("octocat")

    mock_delete.assert_called_once_with(
        f"{BASE_URL}/user/following/octocat",
        headers=BASE_HEADERS,
        timeout=TIME_OUT,
    )




@patch("fgit.requests.get")
def test_see_repos_calls_correct_url(mock_get):
    mock_get.return_value.json.return_value = []
    mock_get.return_value.raise_for_status.return_value = None

    see_repos("octocat")

    mock_get.assert_called_once_with(
        f"{BASE_URL}/users/octocat/repos",
        headers=BASE_HEADERS,
        timeout=TIME_OUT,
    )


@patch("fgit.requests.get")
def test_see_repos_raises_on_failure(mock_get):
    mock_get.return_value.raise_for_status.side_effect = HTTPError("500")

    with pytest.raises(HTTPError):
        see_repos("octocat")