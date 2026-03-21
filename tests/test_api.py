import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT = 10


@pytest.fixture(scope="module")
def post():
    response = requests.get(f"{BASE_URL}/posts", timeout=TIMEOUT)
    return response.json()


@pytest.mark.smoke
@pytest.mark.regression
def test_get_posts_returns_200():
    response = requests.get(f"{BASE_URL}/posts", timeout=TIMEOUT)
    assert response.status_code == 200


@pytest.mark.regression
def test_get_posts_returns_list(post):
    assert isinstance(post, list)
    assert len(post) == 100


@pytest.mark.regression
def test_post_has_correct_fields(post):
    first = post[0]
    assert "id" in first
    assert "title" in first
    assert "body" in first
    assert "userId" in first

    assert isinstance(first["id"], int)
    assert isinstance(first["title"], str)
    assert isinstance(first["body"], str)
    assert isinstance(first["userId"], int)


@pytest.mark.smoke
@pytest.mark.regression
def test_create_post():
    payload = {"title": "Test Post", "body": "Test body", "userId": 1}
    response = requests.post(f"{BASE_URL}/posts", json=payload, timeout=TIMEOUT)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == payload["title"]
    assert created["body"] == payload["body"]


# smoke covers just one ID — all 5 would slow down a quick check
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("post_id", [1])
def test_valid_post_returns_200_smoke(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}", timeout=TIMEOUT)
    assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize("post_id", [2, 3, 50, 100])
def test_valid_post_returns_200(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}", timeout=TIMEOUT)
    assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize("post_id", [0, -1, 99999])
def test_invalid_post_returns_404(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}", timeout=TIMEOUT)
    assert response.status_code == 404


@pytest.mark.regression
@pytest.mark.parametrize(
    ("title", "body", "user_id"),
    [
        ("First post", "Body one", 1),
        ("Second post", "Body two", 2),
        ("", "Empty title post", 1),
    ],
)
def test_create_post_with_different_payloads(title, body, user_id):
    payload = {"title": title, "body": body, "userId": user_id}
    response = requests.post(f"{BASE_URL}/posts", json=payload, timeout=TIMEOUT)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == title
    assert created["userId"] == user_id


@pytest.mark.regression
def test_nonexistent_post_returns_404():
    response = requests.get(f"{BASE_URL}/posts/99999", timeout=TIMEOUT)
    assert response.status_code == 404
