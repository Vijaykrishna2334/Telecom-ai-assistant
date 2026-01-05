/**
 * TypeScript type definitions for Telecom AI Assistant
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  messageType?: 'text' | 'transcription' | 'function_call';
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: number;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  conversation_id: number;
}

export interface Plan {
  id: number;
  plan_id: string;
  name: string;
  price: number;
  data: string;
  calls: string;
  sms: string;
  features: string[];
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface VoiceSession {
  id: number;
  conversation_id: number;
  session_id: string;
  audio_format: string;
  sample_rate: number;
  duration_seconds: number;
  created_at: string;
}

export interface Assistant {
  id: number;
  name: string;
  type: string;
  description: string;
  is_active: boolean;
  created_at: string;
}

export interface HealthCheck {
  status: string;
  version: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'text' | 'audio' | 'control' | 'error';
  data: any;
  timestamp?: string;
}
