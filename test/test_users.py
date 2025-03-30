import pytest
from typing import Generator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.database import get_session
from src.main import app
from src.models import User


# Create a test client
client = TestClient(app)


# Mock the database session
@pytest.fixture
def mock_db() -> Generator[MagicMock, None, None]:
    """Mock the database session."""
    session = MagicMock(spec=Session)

    # Override the dependency for the duration of the test
    app.dependency_overrides[get_session] = lambda: session

    # Yield the session to the test
    yield session

    # Restore the original dependency after the test
    app.dependency_overrides.pop(get_session)


def test_create_user_success(mock_db: MagicMock) -> None:
    """Test creating a user successfully."""
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)

    response = client.post(
        "/users/",
        json={"name": "John Doe", "email": "john.doe@example.com"},
    )
    response_data = response.json()

    assert response.status_code == 200
    assert "created_at" in response_data

    # Remove the created_at and updated_at fields from the response data
    response_data.pop("created_at")
    response_data.pop("updated_at")
    
    assert response_data == {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
    }   


def test_get_users_success(mock_db: MagicMock) -> None:
    """Test getting users successfully."""
    mock_users = [
        User(id=1, name="Alice", email="alice@example.com"),
        User(id=2, name="Bob", email="bob@example.com"),
    ]

    mock_db.exec.return_value.all.return_value = mock_users

    response = client.get("/users/")
    response_data = response.json()

    # Remove the created_at and updated_at fields from each user in the response data
    for user in response_data:
        user.pop("created_at")
        user.pop("updated_at")

    assert response.status_code == 200
    assert response_data == [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]


def test_update_user_email_success(mock_db: MagicMock) -> None:
    """Test updating a user's email successfully."""
    # Create a mock user
    user_id = 1
    name = "Test User"
    old_email = "old@example.com"
    new_email = "new@example.com"
    mock_user = MagicMock(spec=User)
    mock_user.id = user_id
    mock_user.name = name
    mock_user.email = old_email

    # Mock the return value of the database query
    mock_db.exec.return_value.first.return_value = mock_user

    # Call the endpoint
    response = client.put(f"/users/{user_id}?email={new_email}")
    
    # Assert
    assert response.status_code == 200
    assert mock_user.email == new_email
