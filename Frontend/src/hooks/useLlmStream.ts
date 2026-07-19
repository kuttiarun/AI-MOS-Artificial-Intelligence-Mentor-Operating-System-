import { useState, useCallback } from "react";

export interface Message {
  role: "user" | "mentor";
  content: string;
}

export const useLlmStream = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const streamChat = useCallback(
    async (
      userMessage: string,
      currentNodeId: string,
      onChunk: (chunk: string) => void,
      onStart: () => void
    ) => {
      // 1. Fetch credentials from localStorage
      const apiKey = localStorage.getItem("aimos_api_key");
      const provider = localStorage.getItem("aimos_provider");
      const userId = localStorage.getItem("aimos_user_id") || undefined;

      if (!apiKey || !provider) {
        setError("Credentials not found. Please click the key icon to configure BYOK.");
        return false;
      }

      setIsStreaming(true);
      setError(null);
      onStart();

      try {
        // 2. Perform POST request supporting custom headers (solving EventSource limitations)
        const response = await fetch("http://localhost:8000/api/v1/gateway/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-User-API-Key": apiKey,
            "X-User-Provider": provider,
            ...(userId ? { "X-User-Id": userId } : {}),
          },
          body: JSON.stringify({
            current_node_id: currentNodeId,
            user_message: userMessage,
          }),
        });

        // 3. Handle non-200 connection issues (SRS §4 Graceful Key Failures)
        if (!response.ok) {
          let errDetail = `Server returned status ${response.status}`;
          try {
            const errJson = await response.json();
            if (errJson.detail && typeof errJson.detail === "object") {
              errDetail = errJson.detail.detail || errJson.detail.error || errDetail;
            } else if (errJson.detail) {
              errDetail = errJson.detail;
            }
          } catch {
            // Ignore parsing error and use default
          }

          if (response.status === 401) {
            throw new Error(`Authentication Failed: ${errDetail}`);
          }
          if (response.status === 429) {
            throw new Error(`Rate Limited: ${errDetail}`);
          }
          throw new Error(errDetail);
        }

        const body = response.body;
        if (!body) {
          throw new Error("Response body is empty.");
        }

        // 4. Iterate over the stream using a ReadableStream reader
        const reader = body.getReader();
        const decoder = new TextDecoder("utf-8");
        let done = false;
        let buffer = "";

        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;

          if (value) {
            // Decode chunk and add to buffer
            buffer += decoder.decode(value, { stream: !done });
            const lines = buffer.split("\n");

            // Save the last line in the buffer if it is incomplete
            buffer = lines.pop() || "";

            for (const line of lines) {
              const cleanedLine = line.trim();
              if (!cleanedLine) continue;

              // Check for OpenAI SSE standard prefix
              if (cleanedLine.startsWith("data:")) {
                const dataContent = cleanedLine.slice(5).trim();
                if (dataContent === "[DONE]") {
                  done = true;
                  break;
                }

                try {
                  const parsed = JSON.parse(dataContent);
                  const textChunk = parsed.choices?.[0]?.delta?.content;
                  if (textChunk) {
                    onChunk(textChunk);
                  }
                } catch {
                  // Sometimes chunks get cut across boundaries. We skip parsing errors 
                  // on lines, but keeping them buffered would be optimal. 
                  // (Since we split on \n and accumulate incomplete lines in buffer, 
                  // JSON parse failures are rare).
                }
              }
            }
          }
        }
        return true;
      } catch (err: any) {
        setError(err.message || "An unexpected error occurred during streaming.");
        return false;
      } finally {
        setIsStreaming(false);
      }
    },
    []
  );

  return {
    streamChat,
    isStreaming,
    error,
    setError,
  };
};
