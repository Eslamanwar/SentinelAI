const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function startInvestigation(target: string, domain?: string, industry?: string) {
  const response = await fetch(`${API_URL}/api/investigate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target, domain, industry }),
  });

  if (!response.ok) {
    throw new Error(`Investigation failed: ${response.statusText}`);
  }

  return response;
}

export async function getEnvironment() {
  const response = await fetch(`${API_URL}/api/environment`);
  if (!response.ok) throw new Error("Failed to fetch environment");
  return response.json();
}

export async function getThreats() {
  const response = await fetch(`${API_URL}/api/threats`);
  if (!response.ok) throw new Error("Failed to fetch threats");
  return response.json();
}

export function createEventSource(response: Response): ReadableStreamDefaultReader<Uint8Array> | null {
  if (!response.body) return null;
  return response.body.getReader();
}

export interface SSEEvent {
  type: string;
  agent?: string;
  investigation_id?: string;
  threats_found?: number;
  content?: string;
  message?: string;
  timestamp?: string;
}

export async function* parseSSEStream(response: Response): AsyncGenerator<SSEEvent> {
  if (!response.body) return;

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data as SSEEvent;
          } catch {
            // skip malformed JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
