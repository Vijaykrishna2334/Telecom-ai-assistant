/**
 * API client for Telecom AI Assistant backend
 */
import axios, { AxiosInstance } from 'axios';
import type { ChatRequest, ChatResponse, Plan, Assistant, HealthCheck } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health endpoints
  async getHealth(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/health');
    return response.data;
  }

  async getReady(): Promise<any> {
    const response = await this.client.get('/ready');
    return response.data;
  }

  // Chat endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/api/v1/chat', request);
    return response.data;
  }

  // Plan endpoints
  async getPlans(): Promise<Plan[]> {
    const response = await this.client.get<Plan[]>('/api/v1/plans');
    return response.data;
  }

  async getPlan(planId: string): Promise<Plan> {
    const response = await this.client.get<Plan>(`/api/v1/plans/${planId}`);
    return response.data;
  }

  // Assistant endpoints
  async getAssistants(): Promise<Assistant[]> {
    const response = await this.client.get<Assistant[]>('/api/v1/assistants');
    return response.data;
  }

  // Voice endpoints
  async createVoiceSession(userId: number): Promise<any> {
    const response = await this.client.post('/api/v1/voice/sessions', {
      user_id: userId,
      audio_format: 'wav',
      sample_rate: 16000,
    });
    return response.data;
  }

  async getVoiceSession(sessionId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/voice/sessions/${sessionId}`);
    return response.data;
  }

  async deleteVoiceSession(sessionId: string): Promise<void> {
    await this.client.delete(`/api/v1/voice/sessions/${sessionId}`);
  }
}

export const apiClient = new APIClient();
export default apiClient;
