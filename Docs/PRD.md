## Product Requirements Document (PRD) v1.1: AI-MOS MVP

### 1. Project Overview & Vision

* **Project Name:** AI-MOS (Artificial Intelligence Mentor Operating System).


* **Tagline:** Learn. Build. Think. Grow.


* **Mission:** To transform software engineering education by shifting away from standard chat interfaces into a first-principles, adaptive architectural mentor that trains users to become fully independent engineers.


* **Core Architectural Pivot (v1.1 Update):** To ensure infinite scaling and zero platform-side API costs, the system uses a **Bring Your Own Key (BYOK)** model. The platform controls the curriculum logic, system context, and learning memory, while the user provides their own API keys (such as NVIDIA NIM, Google Gemini, or OpenAI) to power the LLM compute layer.

---

### 2. User Personas

* **The Absolute Beginner:** Has no formal computer science background. Prone to "tutorial hell" and over-relying on AI for copy-pasting code without understanding underlying architectural decisions.


* **The Interview Preparer:** A user who possesses academic knowledge or basic syntax familiarity (e.g., preparing for a Java Developer role at Zoho) but struggles with deep problem-solving intuition, system design concepts, and multi-step technical reasoning.



---

### 3. Core Feature Matrix (MVP Scope)

| Module ID | Feature Name | Description | MVP Implementation Scope |
| --- | --- | --- | --- |
| **MOD-01** | **BYOK Setup & Diagnostic Onboarding** | Configures user keys and evaluates their current technical skill baseline.

 | UI configuration dropdown for API keys + a dynamic 10-question evaluation chat. |
| **MOD-02** | **Learning Memory Engine** | Tracks student progress, weak points, and constraints over time.

 | A relational schema connecting user learning state metrics to the backend. |
| **MOD-03** | **First-Principles Learning Engine** | Renders curriculum following a strict pedagogical framework.

 | A markdown rendering client with programmatic validation gates for concepts. |
| **MOD-04** | **Decentralized AI Gateway** | Intercepts UI requests, appends platform context, and executes API calls utilizing the user's local key. | A model-agnostic FastAPI middleware router supporting OpenAI-compatible formats (NVIDIA NIM). |
| **MOD-05** | **The Research Coach Middleware** | Prevents AI model laziness by stripping direct code blocks on initial attempts. | System prompt injection rules that enforce Socratic questioning and link to official documentation. |

---

### 4. Detailed Module Specifications

#### MOD-01: BYOK Configuration & Diagnostic Onboarding

> **Problem:** Hosting AI infrastructure centrally causes massive operational costs. Furthermore, uniform courses ignore individual student constraints and current knowledge baselines.
> 
> 

* **Functional Requirements:**
* The application must present a configuration wizard upon initial launch, prompting the user to select an LLM provider (e.g., NVIDIA NIM, OpenAI, Anthropic, Google AI Studio).
* The system must securely store the user's API key strictly on the client side inside the browser's secure `LocalStorage` space.
* The backend must perform a lightweight validation handshake using the provided key before unlocking the platform.
* Once validated, the system initiates a dynamic diagnostic interview chat to gauge programming logic, hardware constraints, and available weekly time commitments.





#### MOD-02: The Learning Memory Engine

> **Problem:** Standard chat interfaces treat every prompt as an isolated event, forgetting the user's recurring structural patterns and errors.
> 
> 

* **Functional Requirements:**
* The system must maintain a unified database profile tracking the user's active node in the curriculum, technical weak areas, and historical confidence levels.


* If a user consistently fails evaluations on a specific concept (e.g., interface polymorphism or thread synchronization), the memory engine flags this topic as a "High-Risk Weakness".


* The database will maintain operational state profiles across separate tables tracking `User_Profiles`, `Completed_Lessons`, and `Active_Weaknesses`.





#### MOD-03: First-Principles Learning Engine

> **Problem:** Most online tutorials focus heavily on specific code syntax without teaching the contextual engineering decisions behind why those frameworks were created.
> 
> 

* **Functional Requirements:**
* Content presentation must follow the strict structural sequence established in the AI-MOS blueprint: Core Why $\rightarrow$ Problem $\rightarrow$ Analogy $\rightarrow$ Theory $\rightarrow$ Syntax $\rightarrow$ Safe Code Execution.


* Users cannot advance to a subsequent curriculum node until they complete a dual-verification gate: an automated debugging test code box and a text block requiring them to explain the concept back to the mentor in their own words.





#### MOD-04: Decentralized AI Gateway

> **Problem:** Interfacing the frontend directly with variable AI providers breaks system prompt constraints and exposes architecture secrets.

* **Functional Requirements:**
* The user's application frontend sends requests along with the locally stored user API key passed securely via the request headers.
* The FastAPI backend intercepts the payload, aggregates relevant context files from the system markdown knowledge base, and attaches the `User_State` snapshot.


* The gateway translates the aggregated package into the vendor-specific schema (e.g., mapping standard payloads to an OpenAI-compatible structure for direct execution via NVIDIA NIM instances).
* The server streams the returned LLM response tokens back to the client interface to minimize perceived latency.



#### MOD-05: The Research Coach

> **Problem:** AI tools that provide immediate, direct code answers prevent users from developing real debugging skills and self-sufficiency.
> 
> 

* **Functional Requirements:**
* The gateway must systematically parse outgoing system prompts to inject strict pedagogical boundary conditions.


* The model must be explicitly banned from returning complete, copy-pasteable blocks of operational code when a user encounters a compilation error on their first attempt.


* Instead, the response must prioritize Socratic guiding questions, structural pseudocode outlines, and direct instructional formatting tips showing the user how to navigate technical documentation.





---

### 5. Out of Scope for MVP (Deferred to v2.0+)

* **Dynamic Multi-Model Auto-Routing:** The MVP will rely on whichever single model provider the user explicitly connects during onboarding, bypassing dynamic runtime orchestration logic based on token pricing or internal task complexity.
* **Open Market Curriculum Place:** Third-party community lesson contribution loops and shared public roadmaps are excluded from the initial release scope.


* **Automated Portfolio Syncing:** Direct background tracking integration with live GitHub or LinkedIn accounts will be deferred until the core mentorship loop is validated.



---

### 6. Technical Stack Baseline Alignment

* **Frontend:** React with TypeScript and Tailwind CSS for a clean, highly scannable dashboard UI.


* **Backend:** FastAPI (Python) to serve as our lightweight, high-performance AI Gateway orchestration layer.


* **Primary Storage:** PostgreSQL for persistent relational data schemas (tracking student memory, profile matrices, and curriculum structures).



---