/**
 * Centralized API Configuration
 *
 * This module provides environment-based API URLs so you can deploy
 * to different environments without changing code.
 *
 * Configure URLs via environment variables:
 * - VITE_API_URL: REST API base URL (default: http://localhost:8080)
 * - VITE_WS_URL: WebSocket base URL (default: ws://localhost:8080)
 */

export const API_CONFIG = {
    /** Base URL for REST API calls */
    BASE_URL: import.meta.env.VITE_API_URL || "http://localhost:8080",
    /** Base URL for WebSocket connections */
    WS_URL: import.meta.env.VITE_WS_URL || "ws://localhost:8080",
} as const;

/** REST API endpoints */
export const API_ENDPOINTS = {
    /** Standard chat endpoint (full response) */
    CHAT: `${API_CONFIG.BASE_URL}/api/v1/chat`,
    /** Streaming chat endpoint (word-by-word response) */
    CHAT_STREAM: `${API_CONFIG.BASE_URL}/api/v1/chat/stream`,
    /** Health check endpoint */
    HEALTH: `${API_CONFIG.BASE_URL}/health`,
} as const;

/** WebSocket endpoints */
export const WS_ENDPOINTS = {
    /** Voice realtime WebSocket connection */
    VOICE: (sessionId: string) =>
        `${API_CONFIG.WS_URL}/ws/voice/realtime/${sessionId}`,
} as const;
