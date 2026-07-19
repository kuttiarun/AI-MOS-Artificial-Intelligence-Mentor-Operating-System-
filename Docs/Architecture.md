## AI-MOS Backend Architecture Blueprint v1.0

### 1. Project Directory Structure

Here is how the repository layout looks for our FastAPI (`backend/`) directory:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point & middleware config
│   ├── core/
│   │   ├── config.py           # Environment settings & security variables
│   │   └── database.py         # SQLAlchemy / PostgreSQL connection setup
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py     # Session tracking & user onboarding
│   │       │   ├── gateway.py  # The BYOK LLM streaming gateway router
│   │       │   └── curriculum.py # Checkpoints and node progress controllers
│   │       └── api.py          # Accumulator for v1 router registrations
│   ├── schemas/
│   │   └── gateway.py          # Pydantic validation models
│   └── services/
│       └── llm_factory.py      # Agnostic client orchestrator (NVIDIA NIM, Gemini, etc.)
├── requirements.txt
└── .env

```

---

### 2. Core Implementation: FastAPI Gateway Boilerplate

Below is the production-ready code foundation for the stateless, decentralized **AI Gateway Engine**.

#### `app/schemas/gateway.py`

Defines the structure of incoming interaction payloads.

```python
from pydantic import BaseModel, Field

class ChatPayload(BaseModel):
    current_node_id: str = Field(..., example="java-collections-hashmap")
    user_message: str = Field(..., min_length=1, example="Why does an array resize?")

```

#### `app/services/llm_factory.py`

Dynamically instantiates LLM clients using the user's browser-supplied API credentials on a per-request basis.

```python
import httpx
from fastapi import HTTPException

class LLMFactory:
    @staticmethod
    async def get_streaming_response(provider: str, api_key: str, payload: dict, system_prompt: str):
        """
        Routes the compiled request containing curriculum context directly to the 
        user's target compute provider without writing keys to disk or logs.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload["user_message"]}
        ]

        if provider == "nvidia-nim":
            # NVIDIA NIM exposes an OpenAI-compliant endpoint format
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # Defaulting to an optimal general reasoning open model available on NIM
            data = {
                "model": "meta/llama-3.1-70b-instruct", 
                "messages": messages,
                "stream": True
            }
            
            # Use an asynchronous HTTP client to handle the server-sent events stream
            client = httpx.AsyncClient()
            try:
                # We return the raw stream generator directly back to the route handler
                req = client.build_request("POST", url, headers=headers, json=data)
                response = await client.send(req, stream=True)
                
                if response.status_code != 200:
                    await response.aread()
                    raise HTTPException(status_code=response.status_code, detail="Upstream provider error.")
                
                return response
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to reach LLM Provider: {str(e)}")
        
        else:
            raise HTTPException(status_code=400, detail=f"LLM Provider '{provider}' is not supported yet.")

```

#### `app/api/v1/endpoints/gateway.py`

Manages route handling, pulls local system context from files, and builds the strict pedagogical context wrapper.

```python
from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.schemas.gateway import ChatPayload
from app.services.llm_factory import LLMFactory

router = APIRouter()

# Simple mock for pulling system context. In production, this reads from markdown/DB
def get_curriculum_context(node_id: str) -> str:
    return f"[Curriculum Module: {node_id}] Explain rules clearly without writing complete code blocks."

@router.post("/chat")
async def stream_mentor_chat(
    payload: ChatPayload,
    x_user_api_key: str = Header(..., description="User provided LLM developer token"),
    x_user_provider: str = Header(..., description="Target compute provider instance")
):
    """
    Accepts student prompt payloads, injects educational context guidelines, 
    and streams responses using the user's localized API key validation.
    """
    # 1. Gather historical baseline and context data
    lesson_context = get_curriculum_context(payload.current_node_id)
    
    # 2. Enforce the strict "Research Coach / Anti-Laziness" prompting guidelines
    pedagogical_prompt = (
        f"{lesson_context}\n"
        "You are the AI-MOS software engineering mentor. Adhere to these exact parameters:\n"
        "- Adopt a Socratic teaching style.\n"
        "- Do not provide immediate copy-pasteable blocks of functional code under any circumstance.\n"
        "- Structure your explanation around real-world analogies.\n"
        "- Provide architectural breadcrumbs and reference documentation hints to encourage critical thinking."
    )
    
    # 3. Call the compute factory layer
    provider_response = await LLMFactory.get_streaming_response(
        provider=x_user_provider,
        api_key=x_user_api_key,
        payload=payload.dict(),
        system_prompt=pedagogical_prompt
    )
    
    # 4. Stream token frames continuously back to the frontend application
    async def event_generator():
        async for chunk in provider_response.aiter_raw():
            yield chunk
        await provider_response.aclose()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

```

#### `app/main.py`

Stitches our application routers together and handles cross-origin network orchestration.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import gateway

app = FastAPI(
    title="AI-MOS Gateway",
    description="Stateless BYOK Orchestration and Context Injection Framework",
    version="1.0.0"
)

# Configure open-source standard communication properties
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust explicitly to your domain URL wrapper during hosting
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route attachment
app.include_router(gateway.router, prefix="/api/v1/gateway", tags=["AI Gateway"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "AI-MOS FastAPI Gateway"}

```