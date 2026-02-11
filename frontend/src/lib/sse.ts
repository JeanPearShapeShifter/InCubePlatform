// InCube Platform — SSE (Server-Sent Events) client helper

export interface SSEEvent {
  event: string;
  data: string;
}

export interface SSEOptions {
  onEvent: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

/**
 * Connect to an SSE endpoint and stream events.
 * Returns an AbortController to cancel the connection.
 */
export function connectSSE(url: string, options: SSEOptions): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(url, {
        credentials: "include",
        headers: { Accept: "text/event-stream" },
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`SSE connection failed: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("SSE response has no body");
      }

      options.onOpen?.();

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // Keep incomplete last line in buffer
        buffer = lines.pop() ?? "";

        let currentEvent = "";
        let currentData = "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            currentData = line.slice(5).trim();
          } else if (line === "") {
            // Empty line = end of event
            if (currentData) {
              options.onEvent({
                event: currentEvent || "message",
                data: currentData,
              });
            }
            currentEvent = "";
            currentData = "";
          }
        }
      }

      options.onClose?.();
    } catch (err) {
      if (controller.signal.aborted) return;
      options.onError?.(
        err instanceof Error ? err : new Error("SSE connection error"),
      );
    }
  })();

  return controller;
}
