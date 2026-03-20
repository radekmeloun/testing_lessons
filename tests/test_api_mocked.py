import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


def test_create_post_mocked(mocker):
    # Define the fake response object
    mock_response = mocker.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 101,
        "title": "Test Post",
        "body": "Test body",
        "userId": 1,
    }

    # Replace requests.post with our fake — only for this test
    mocker.patch("requests.post", return_value=mock_response)

    # Call the code under test — no network happens
    payload = {"title": "Test Post", "body": "Test body", "userId": 1}
    response = requests.post(f"{BASE_URL}/posts", json=payload)

    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Test Post"
    assert created["id"] == 101


def test_get_posts_mocked(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "title": "First", "body": "Body", "userId": 1},
        {"id": 2, "title": "Second", "body": "Body", "userId": 1},
    ]

    mocker.patch("requests.get", return_value=mock_response)

    response = requests.get(f"{BASE_URL}/posts")

    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 2
    assert posts[0]["title"] == "First"


def test_create_post_called_with_correct_payload(mocker):
    mock_post = mocker.patch("requests.post", return_value=mocker.Mock(status_code=201))

    payload = {"title": "Test Post", "body": "Test body", "userId": 1}
    requests.post(f"{BASE_URL}/posts", json=payload)

    # Verify requests.post was called exactly once with the right arguments
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["title"] == "Test Post"


def test_api_failure_handling(mocker):
    """Test how your code handles a 500 response — impossible to test reliably without mocking."""
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}

    mocker.patch("requests.post", return_value=mock_response)

    response = requests.post(f"{BASE_URL}/posts", json={})

    assert response.status_code == 500
