"""Log-injection and SSRF guards in services/github_fetcher.py."""

import pytest

from services.github_fetcher import _sanitize_for_log, _validate_github_endpoint


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("normal_username", "normal_username"),
        ("user\nADMIN", "userADMIN"),
        ("user\r\nADMIN", "userADMIN"),
        ("user\x00admin", "useradmin"),
        ("tab\there", "tab here"),
        ("", ""),
    ],
)
def test_sanitize_for_log_strips_control_characters(value, expected):
    assert _sanitize_for_log(value) == expected


@pytest.mark.parametrize(
    ("endpoint", "expected"),
    [
        ("users/testuser", "users/testuser"),
        ("/repos/owner/repo/languages/", "repos/owner/repo/languages"),
        (
            "users/testuser/repos?per_page=100&page=2",
            "users/testuser/repos?per_page=100&page=2",
        ),
    ],
)
def test_validate_endpoint_accepts_github_paths(endpoint, expected):
    assert _validate_github_endpoint(endpoint) == expected


@pytest.mark.parametrize(
    "endpoint",
    [
        "",
        "users/../admin",
        "http://evil.com/api",
        "//evil.com/api",
        "users/test user",
        "users/test@evil.com",
    ],
)
def test_validate_endpoint_blocks_unsafe_input(endpoint):
    with pytest.raises(ValueError):
        _validate_github_endpoint(endpoint)
