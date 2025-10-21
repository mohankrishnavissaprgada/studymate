import type { ChatResponse } from '../types';

const API_BASE_URL = 'http://localhost:5000';

export async function sendMessage(query: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error('Failed to get response from server');
  }

  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
