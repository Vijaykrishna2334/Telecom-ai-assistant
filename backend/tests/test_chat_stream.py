"""
Tests for Streaming Chat API endpoint.

These tests verify the streaming chat functionality:
- SSE response format
- Token streaming
- Error handling in streams
"""
import pytest
from fastapi.testclient import TestClient


class TestStreamingChatEndpoint:
    """Tests for the /api/v1/chat/stream endpoint."""

    def test_stream_chat_returns_sse_content_type(self, client: TestClient) -> None:
        """Test that streaming endpoint returns SSE content type."""
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "Hello",
                "session_id": "test-stream-123",
            },
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

    def test_stream_chat_returns_sse_format(self, client: TestClient) -> None:
        """Test that streaming response is in SSE format."""
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "Hello",
                "session_id": "test-stream-format",
            },
        )
        
        assert response.status_code == 200
        content = response.text
        
        # SSE format should have "data:" prefix
        assert "data:" in content

    def test_stream_chat_with_session_id(self, client: TestClient) -> None:
        """Test that streaming chat respects session ID."""
        session_id = "stream-session-456"
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "What plans do you offer?",
                "session_id": session_id,
            },
        )
        
        assert response.status_code == 200
        # Session ID should be included in the streamed data
        assert session_id in response.text

    def test_stream_chat_handles_empty_message(self, client: TestClient) -> None:
        """Test that stream chat validates empty messages."""
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "",
                "session_id": "test-stream-empty",
            },
        )
        
        # Should return 422 (Validation Error) for empty message
        assert response.status_code == 422

    def test_stream_chat_with_history(self, client: TestClient) -> None:
        """Test that stream chat accepts conversation history."""
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "Tell me more",
                "session_id": "test-stream-history",
                "history": [
                    {"role": "user", "content": "What is your cheapest plan?"},
                    {"role": "assistant", "content": "Our basic plan starts at..."},
                ],
            },
        )
        
        assert response.status_code == 200
        assert "data:" in response.text


class TestStreamingChatValidation:
    """Tests for streaming chat request validation."""

    def test_stream_missing_message(self, client: TestClient) -> None:
        """Test that missing message field is rejected."""
        response = client.post(
            "/api/v1/chat/stream",
            json={"session_id": "test-123"},
        )
        
        assert response.status_code == 422

    def test_stream_generates_session_id(self, client: TestClient) -> None:
        """Test that stream generates session ID if not provided."""
        response = client.post(
            "/api/v1/chat/stream",
            json={"message": "Hello"},
        )
        
        assert response.status_code == 200
        # Should have generated a session_id in the response
        assert "session_id" in response.text
