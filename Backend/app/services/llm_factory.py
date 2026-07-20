"""
AI-MOS Backend — LLM Factory Service
======================================
Model-agnostic LLM client orchestrator implementing the BYOK
(Bring Your Own Key) pattern.

Standardizes all output streaming streams into unified OpenAI-compatible
SSE line structures:
`data: {"choices": [{"delta": {"content": "text_chunk"}}]}\n\n`
"""

import json
import logging
import httpx
from typing import AsyncGenerator
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Provider endpoint registry
_PROVIDER_ENDPOINTS: dict[str, str] = {
    "nvidia-nim": "https://integrate.api.nvidia.com/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "google-gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent",
    "anthropic": "https://api.anthropic.com/v1/messages",
}

# Default models
_DEFAULT_MODELS: dict[str, str] = {
    "nvidia-nim": "meta/llama-3.1-70b-instruct",
    "openai": "gpt-4o-mini",
    "google-gemini": "gemini-2.5-flash",
    "anthropic": "claude-3-5-sonnet-20241022",
}


class LLMFactory:
    """
    Executes REST-based API streams using the user's supplied BYOK key.
    Returns a standardized AsyncGenerator yielding OpenAI-compatible SSE strings.
    """

    @staticmethod
    async def get_streaming_response(
        provider: str,
        api_key: str,
        payload: dict,
        system_prompt: str,
    ) -> AsyncGenerator[str, None]:
        """
        Main router routing requests to NVIDIA, OpenAI, Gemini, or Anthropic.
        Returns a standardized SSE generator.
        """
        provider = provider.strip().lower()

        # Clean and validate API key to prevent sending invalid "Bearer " or empty headers
        api_key_clean = api_key.strip()
        if not api_key_clean:
            raise HTTPException(
                status_code=401,
                detail="API key configuration is missing or empty. Please check your compute provider settings."
            )

        if provider not in _PROVIDER_ENDPOINTS:
            supported = ", ".join(_PROVIDER_ENDPOINTS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{provider}' is not supported. Supported: [{supported}]."
            )

        if provider == "nvidia-nim":
            return LLMFactory._stream_openai_compatible(
                endpoint=_PROVIDER_ENDPOINTS["nvidia-nim"],
                api_key=api_key_clean,
                model=_DEFAULT_MODELS["nvidia-nim"],
                user_msg=payload["user_message"],
                system_prompt=system_prompt
            )
        
        elif provider == "openai":
            return LLMFactory._stream_openai_compatible(
                endpoint=_PROVIDER_ENDPOINTS["openai"],
                api_key=api_key_clean,
                model=_DEFAULT_MODELS["openai"],
                user_msg=payload["user_message"],
                system_prompt=system_prompt
            )

        elif provider == "google-gemini":
            return LLMFactory._stream_gemini(
                endpoint=_PROVIDER_ENDPOINTS["google-gemini"],
                api_key=api_key_clean,
                user_msg=payload["user_message"],
                system_prompt=system_prompt
            )

        elif provider == "anthropic":
            return LLMFactory._stream_anthropic(
                endpoint=_PROVIDER_ENDPOINTS["anthropic"],
                api_key=api_key_clean,
                model=_DEFAULT_MODELS["anthropic"],
                user_msg=payload["user_message"],
                system_prompt=system_prompt
            )

        raise HTTPException(status_code=400, detail="Unknown provider.")

    @staticmethod
    async def _stream_openai_compatible(
        endpoint: str,
        api_key: str,
        model: str,
        user_msg: str,
        system_prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Streams from OpenAI or NVIDIA NIM endpoints."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "stream": True,
            "temperature": 0.6,
            "max_tokens": 2048
        }
        timeout = httpx.Timeout(connect=30.0, read=None, write=30.0, pool=30.0)
        client = httpx.AsyncClient(timeout=timeout)

        try:
            request = client.build_request("POST", endpoint, headers=headers, json=body)
            response = await client.send(request, stream=True)
            LLMFactory._verify_status_code(response.status_code)

            async for line in response.aiter_lines():
                if line:
                    yield f"{line}\n"
        finally:
            await client.aclose()

    @staticmethod
    async def _stream_anthropic(
        endpoint: str,
        api_key: str,
        model: str,
        user_msg: str,
        system_prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Streams from Anthropic Claude API translating SSE events to OpenAI format."""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        body = {
            "model": model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_msg}
            ],
            "max_tokens": 2048,
            "temperature": 0.6,
            "stream": True
        }
        timeout = httpx.Timeout(connect=30.0, read=None, write=30.0, pool=30.0)
        client = httpx.AsyncClient(timeout=timeout)

        try:
            request = client.build_request("POST", endpoint, headers=headers, json=body)
            response = await client.send(request, stream=True)
            LLMFactory._verify_status_code(response.status_code)

            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                # Dynamic check: support line starting with 'data:' or raw JSON
                data_str = line
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                
                if data_str == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                try:
                    data = json.loads(data_str)
                    text = ""
                    if data.get("type") == "content_block_delta" and "delta" in data:
                        text = data["delta"].get("text", "")
                    elif "delta" in data and "text" in data["delta"]:
                        text = data["delta"]["text"]
                    
                    if text:
                        sse_payload = {
                            "choices": [{"delta": {"content": text}}]
                        }
                        yield f"data: {json.dumps(sse_payload)}\n\n"
                    elif data.get("type") == "message_stop":
                        yield "data: [DONE]\n\n"
                except Exception:
                    pass
        finally:
            await client.aclose()

    @staticmethod
    async def _stream_gemini(
        endpoint: str,
        api_key: str,
        user_msg: str,
        system_prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Streams from Google AI Studio Gemini API translating JSON buffers to OpenAI format."""
        url = f"{endpoint}?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "contents": [
                {
                    "parts": [{"text": f"System Instructions:\n{system_prompt}\n\nUser Message: {user_msg}"}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "temperature": 0.6
            }
        }
        timeout = httpx.Timeout(connect=30.0, read=None, write=30.0, pool=30.0)
        client = httpx.AsyncClient(timeout=timeout)

        try:
            request = client.build_request("POST", url, headers=headers, json=body)
            response = await client.send(request, stream=True)
            LLMFactory._verify_status_code(response.status_code)

            buffer = ""
            async for raw_chunk in response.aiter_text():
                buffer += raw_chunk
                
                # Check for line structure dynamically
                lines = buffer.split("\n")
                # Keep the last line in the buffer in case it is incomplete
                buffer = lines.pop() if lines else ""
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Clean up array punctuation from stream
                    cleaned = line
                    if cleaned.startswith("["):
                        cleaned = cleaned[1:].strip()
                    if cleaned.endswith("]"):
                        cleaned = cleaned[:-1].strip()
                    if cleaned.startswith(","):
                        cleaned = cleaned[1:].strip()
                    if cleaned.endswith(","):
                        cleaned = cleaned[:-1].strip()
                    
                    if not cleaned:
                        continue
                    
                    try:
                        data = json.loads(cleaned)
                        if "candidates" in data and len(data["candidates"]) > 0:
                            text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                            if text:
                                sse_payload = {
                                    "choices": [{"delta": {"content": text}}]
                                }
                                yield f"data: {json.dumps(sse_payload)}\n\n"
                    except Exception:
                        # Fallback: re-add to buffer for brace matching
                        buffer = line + "\n" + buffer
                
                # Fallback brace matching for multiline chunks
                while True:
                    first_brace = buffer.find("{")
                    if first_brace == -1:
                        break
                    
                    depth = 0
                    last_brace = -1
                    for i in range(first_brace, len(buffer)):
                        if buffer[i] == '{':
                            depth += 1
                        elif buffer[i] == '}':
                            depth -= 1
                            if depth == 0:
                                last_brace = i
                                break
                    
                    if last_brace == -1:
                        break
                    
                    json_str = buffer[first_brace : last_brace + 1]
                    buffer = buffer[last_brace + 1 :]
                    try:
                        data = json.loads(json_str)
                        if "candidates" in data and len(data["candidates"]) > 0:
                            text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                            if text:
                                sse_payload = {
                                    "choices": [{"delta": {"content": text}}]
                                }
                                yield f"data: {json.dumps(sse_payload)}\n\n"
                    except Exception:
                        pass
            
            # Send done chunk
            yield "data: [DONE]\n\n"
        finally:
            await client.aclose()

    @staticmethod
    async def extract_content_from_stream(event_stream: AsyncGenerator[str, None]) -> str:
        """
        Drains the event stream and extracts text tokens dynamically,
        checking the response line structures to unpack the text tokens
        properly based on the active provider. Handles both SSE data-prefixed
        lines and raw JSON frames.
        """
        accumulated = ""
        async for raw_chunk in event_stream:
            for line in raw_chunk.split("\n"):
                line = line.strip()
                if not line:
                    continue
                
                # Check for SSE 'data:' prefix
                data_content = line
                if line.startswith("data:"):
                    data_content = line[5:].strip()
                
                if data_content == "[DONE]":
                    break
                
                try:
                    parsed = json.loads(data_content)
                    token = ""
                    # 1. Check standard OpenAI format (choices[0].delta.content)
                    if "choices" in parsed and len(parsed["choices"]) > 0:
                        choice = parsed["choices"][0]
                        if "delta" in choice:
                            token = choice["delta"].get("content", "")
                        elif "message" in choice:
                            token = choice["message"].get("content", "")
                    # 2. Check Anthropic format (delta.text or content_block_delta type)
                    elif parsed.get("type") == "content_block_delta" and "delta" in parsed:
                        token = parsed["delta"].get("text", "")
                    elif "delta" in parsed and "text" in parsed["delta"]:
                        token = parsed["delta"]["text"]
                    # 3. Check Gemini format (candidates[0].content.parts[0].text)
                    elif "candidates" in parsed and len(parsed["candidates"]) > 0:
                        cand = parsed["candidates"][0]
                        if "content" in cand and "parts" in cand["content"] and len(cand["content"]["parts"]) > 0:
                            token = cand["content"]["parts"][0].get("text", "")
                    
                    accumulated += token
                except Exception:
                    pass
        return accumulated

    @staticmethod
    def _verify_status_code(status_code: int) -> None:
        """Helper raising HTTP exception for bad status codes."""
        if status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Upstream API key authentication failed."
            )
        elif status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Upstream rate limit exceeded."
            )
        elif status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Upstream provider error (HTTP {status_code})."
            )
