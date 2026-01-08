"""
Tests for Chat API endpoints.

These tests verify the chat functionality works correctly:
- Basic chat request/response
- Session ID handling
- Error handling
- Response format validation
"""
import pytest
from fastapi.testclient import TestClient


class TestChatEndpoint:
    """Tests for the /api/v1/chat endpoint."""

    def test_chat_responds_to_message(self, client: TestClient) -> None:
        """Test that chat endpoint responds to a basic message."""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Hello, how are you?",
                "session_id": "test-session-123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert "session_id" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_chat_returns_session_id(self, client: TestClient) -> None:
        """Test that chat returns the provided session ID."""
        session_id = "my-unique-session-456"
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "What plans do you have?",
                "session_id": session_id,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

    def test_chat_generates_session_id_if_not_provided(self, client: TestClient) -> None:
        """Test that chat generates a session ID if none is provided."""
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_chat_handles_empty_message(self, client: TestClient) -> None:
        """Test that chat properly validates empty messages."""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "",  # Empty message should be rejected
                "session_id": "test-123",
            },
        )
        
        # Should return 422 (Validation Error) for empty message
        assert response.status_code == 422

    def test_chat_with_history(self, client: TestClient) -> None:
        """Test that chat accepts conversation history."""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "And what about data limits?",
                "session_id": "test-history-789",
                "history": [
                    {"role": "user", "content": "Tell me about your plans"},
                    {"role": "assistant", "content": "We have various mobile plans..."},
                ],
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_chat_response_has_rag_context(self, client: TestClient) -> None:
        """Test that chat response includes RAG context for debugging."""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "What mobile plans are available?",
                "session_id": "test-rag-context",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        # rag_context should be present (may be None if no relevant docs found)
        assert "rag_context" in data


class TestChatRequestValidation:
    """Tests for chat request validation."""

    def test_missing_message_field(self, client: TestClient) -> None:
        """Test that missing message field is rejected."""
        response = client.post(
            "/api/v1/chat",
            json={"session_id": "test-123"},
        )
        
        assert response.status_code == 422

    def test_invalid_json_format(self, client: TestClient) -> None:
        """Test that invalid JSON is rejected."""
        response = client.post(
            "/api/v1/chat",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )
        
        assert response.status_code == 422

    def test_message_must_be_string(self, client: TestClient) -> None:
        """Test that message must be a string."""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": 12345,  # Number instead of string
                "session_id": "test-123",
            },
        )
        
        assert response.status_code == 422
