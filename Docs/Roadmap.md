## AI-MOS Development Roadmap & WBS (14-Day MVP Sprint)

### Phase 1: Persistence Setup & Core Backend Routing (Days 1–4)

**Objective:** Establish the local infrastructure, execute the database schema, and verify basic endpoint accessibility.

* **Day 1: Repository Initialization & Environment Configuration**
* Set up the standard modular directory structures for both the React/TypeScript frontend and the FastAPI backend.


* Configure structural environment validation schemas using `pydantic-settings` to manage CORS origins and database connection parameters.




* **Day 2: Database Migration & Schema Seeding**
* Execute the production-grade PostgreSQL DDL scripts to create the structural tables (`users`, `curriculum_nodes`, `user_progress`, `weak_areas`) and performance indexes.


* Seed the `curriculum_nodes` table with an initial sequence map representing the baseline curriculum phases.




* **Day 3: Authentication & Session Gateways**
* Implement secure JWT-based authentication endpoints (`/api/v1/auth/signup` and `/api/v1/auth/login`).


* Build the request token extraction middleware to verify active sessions before routing user events.


* **Day 4: Stateless AI Gateway Integration**
* Deploy the `LLMFactory` class to parse incoming request headers for the student's personal `X-User-API-Key` and `X-User-Provider` targets.


* Verify routing functionality using API testing tools to confirm the system safely handles and drops credentials in memory without logging them.





---

### Phase 2: Knowledge Extraction & Socratic Prompt Engineering (Days 5–8)

**Objective:** Connect the local curriculum Markdown repository to the streaming AI engine while locking down structural pedagogical constraints.

```text
[Day 5: Markdown Engine] ──► [Day 6: Context Injection] ──► [Day 7: SSE Streaming] ──► [Day 8: Research Coach Rules]

```

* **Day 5: Markdown Knowledge Engine Storage**
* Populate a localized directory structure with targeted curriculum content modules written in standard Markdown format.


* Build an asynchronous file utility layer in FastAPI to dynamically fetch file contents based on specific lesson parameters.




* **Day 6: Context Aggregation Logic**
* Write the database orchestration layer to retrieve the user's explicit profile history and active weakness flags upon each request.


* Develop a context assembler that seamlessly merges curriculum text contents with the student's unique active learning metrics.




* **Day 7: Server-Sent Events (SSE) Streaming Core**
* Wire up the FastAPI endpoint `/api/v1/gateway/chat` using `StreamingResponse`.


* Establish smooth chunk-by-chunk event delivery pipelines directly from an OpenAI-compatible interface, such as an NVIDIA NIM compute network.




* **Day 8: Research Coach Prompt Optimization**
* Implement boundary condition prompt safeguards within the gateway to structurally ban the model from outputting direct code blocks on a user's initial errors.


* Test validation guardrails to ensure the assistant accurately provides architectural hints and links to official documentation instead of shortcuts.





---

### Phase 3: Split-Screen Interface Workspace Setup (Days 9–11)

**Objective:** Construct a highly responsive, developer-oriented UI dashboard to visually separate reading materials from the conversational dialogue loop.

* **Day 9: Layout System Assembly**
* Build the master three-column layout workspace utilizing Tailwind CSS grid abstractions.


* Implement side-by-side view panes featuring a collapsible file navigation utility alongside an educational text canvas.




* **Day 10: Local Credentials Management Interface**
* Construct the interactive Bring Your Own Key (BYOK) modal dialog component.


* Configure secure browser client-side `LocalStorage` synchronization handlers, keeping secrets fully isolated within the user's environment.




* **Day 11: SSE Streaming Interface Hookup**
* Develop custom React hooks using standard browser API utilities (`fetch` or `EventSource`) to capture streaming chunks from the backend.
* Integrate a markdown component layer to smoothly render incoming conversational tokens in real time.



---

### Phase 4: Validation Gates & End-to-End Testing (Days 12–14)

**Objective:** Tie the user interface elements directly into backend verification gates and run exhaustive system validation checks.

* **Day 12: Knowledge Verification Components**
* Build the custom layout interfaces for the interactive description inputs and simple code block compilation targets.


* Connect the confirmation submit button actions straight to the backend validator endpoint `/api/v1/curriculum/validate`.




* **Day 13: Progress Synchronization Tests**
* Validate the database synchronization loops that update status scores or create new weakness indicators based on assessment results.


* Confirm that passing an evaluation gate successfully transitions a topic node from an active state to a verified completion status.




* **Day 14: End-to-End Integration Sweep**
* Conduct rigorous integration runs simulating a new user entering an arbitrary API key, accessing the system, and navigating lessons.


* Run performance scans to verify sub-millisecond data query processing overhead times across indexed paths.





---