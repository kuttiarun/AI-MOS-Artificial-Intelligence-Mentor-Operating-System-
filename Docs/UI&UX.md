---

## AI-MOS UI/UX Design Specification v1.0

### 1. Workspace Layout Architecture

The interface follows a strict three-column layout designed to maximize screen space, emphasize scannability, and reduce contextual switching overhead.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🌐 AI-MOS Dashboard  [Phase 4: Collections] 🟢 NVIDIA NIM Connected         │
├───────────┬─────────────────────────────────────┬───────────────────────────┤
│ 📁 Intro  │                                     │                           │
│ 📁 Arrays │ 📑 Lesson: HashMap Internals         │ 🤖 Socratic Mentor        │
│ 📁 Lists  │                                     │                           │
│ ➡️ HashMap │ [ The Core "Why" ]                  │ Learner: Why do we use    │
│           │ A HashMap maps keys to values...    │ prime numbers for hashes? │
│           │                                     │                           │
│           │ [ Interactive Playground ]          │ Mentor: Excellent query!  │
│           │ ┌─────────────────────────────────┐ │ Think about modulo math.  │
│           │ │ public class CustomMap { ... }  │ │ What happens if we divide │
│           │ └─────────────────────────────────┘ │ by an even number?        │
│           │                                     │                           │
│           ├─────────────────────────────────────┼───────────────────────────┤
│           │ ⚙️ Code Evaluation Output           │ 💬 [Type response...]     │
└───────────┴─────────────────────────────────────┴───────────────────────────┘

```

* **Left Sidebar (15% Width) - The Curriculum Navigation Tree:** Displays the structured timeline hierarchy (Phases and Lesson Nodes). Checked items indicate fully verified nodes, locked sections display lock badges, and highlighted blocks show the active study node.


* **Center Canvas (50% Width) - The Knowledge Engine Display:** Renders the platform's markdown curriculum files. Includes high-contrast code visualization containers and a sandboxed interactive input arena where the user writes code blocks or edits files.


* **Right Panel (35% Width) - The Socratic Mentorship Console:** Dedicated entirely to the real-time dialogue loop powered by the user's local API key. This pane remains operational independently of changes or content scrolling in the center canvas.



---

### 2. Design Tokens & Theme Configuration (Tailwind CSS Base)

We will leverage a high-contrast dark palette tailored for long coding sessions, emphasizing structural readability.

| Token Type | Utility Class / Value | Architectural Purpose |
| --- | --- | --- |
| **Background (Base)** | `bg-slate-950` | Primary desktop background canvas layer. |
| **Background (Surface)** | `bg-slate-900` | Applied to the console sidebar and conversation block panels. |
| **Primary Borders** | `border-slate-800` | Clean structural dividing rules between open panels. |
| **Accent Tech Alert** | `text-emerald-400` | Applied to verified concepts, passed validations, and active connection status logs.

 |
| **Warning / Risk Alert** | `text-amber-400` | Applied to user-specific weak area components and loop exception alerts.

 |
| **Text Primary** | `text-slate-100` | Standard educational reading copy visibility. |

---

### 3. Core Component Workflows & Wireframe States

#### Component A: BYOK Configuration Gate (Modal Overlay)

When a user launches the app without a validated local key, a modal overrides the display:

* **Provider Selector:** A clean form dropdown element mapping options to configured system providers (e.g., *NVIDIA NIM, OpenAI, Anthropic, Google AI Studio*).


* **Key Security Disclaimer:** A persistent callout card explicitly reinforcing safety:
> 🔒 **Security Notice:** Your API keys are processed strictly inside your local browser storage engine. Our platform servers never store, replicate, or monitor your private API keys.
> 
> 



#### Component B: The "Explanation" Validation Interface

Located at the bottom of the Center Canvas, this step acts as the interactive checkpoint gate before unlocking subsequent nodes.

* **Prompt Instruction:** *"In your own words, explain the structural difference between a Class and an Interface to the mentor."*

* **Action Element:** A simple, distraction-free markdown text area editor block.
* **Status Indicators:** Upon submission, a loading indicator animates while the gateway evaluates the text against the model. If verified, the border shifts to green (`border-emerald-500`) and highlights a *"Proceed to Next Lesson"* primary navigation trigger.



---

### 4. Interactive UX Principles (Anti-Laziness Countermeasures)

To keep the application highly educational and distinct from lazy autocomplete platforms, we enforce the following interactive constraints:

* **Copy-Paste Mitigation:** The Center Canvas code display snippets block manual copy commands via simple CSS styling constraints (`user-select: none`). This requires users to manually type code snippets into the evaluation engine to build foundational muscle memory.
* **Dialogue Anchoring:** Clicking code snippet references within the mentor panel automatically snaps the Center Canvas scroll viewport directly to the matching curriculum code block, maintaining consistent context across panels.

---