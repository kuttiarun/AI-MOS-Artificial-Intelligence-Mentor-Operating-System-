# AI-MOS (AI Mentor Operating System) v2.0
### Open Standard for AI-Driven Education

---

> **"Don't just learn technology. Learn how engineers think."**
> 
> AI-MOS v2.0 is an AI-independent open standard for personalized Socratic software engineering mentorship. Instead of a single model prompt, AI-MOS represents a versioned, modular, and collaborative roadmap designed to build true engineering intuition and real-world problem-solving skills across any LLM platform.

---

## 🧭 Directory Matrix

This specification is broken down into structured books and chapters to allow modular reference and step-by-step contributions:

### [Book 1 — Foundation](book-1-foundation/)
* **Chapter 1**: [Mission & Philosophy](book-1-foundation/01-mission-and-philosophy.md)
* **Chapter 2**: [Mentor Identity](book-1-foundation/02-mentor-identity.md)
* **Chapter 3**: [Golden Rules](book-1-foundation/03-golden-rules.md)
* **Chapter 4**: [Teaching Principles](book-1-foundation/04-teaching-principles.md)

### Book 2 — Student Discovery
* **Chapter 5**: Career Discovery
* **Chapter 6**: Skill Assessment
* **Chapter 7**: Learning Style Detection
* **Chapter 8**: OS & Hardware Assessment
* **Chapter 9**: English Level Assessment
* **Chapter 10**: Budget Assessment

### Book 3 — Teaching Engine
* **Chapter 11**: First Principles
* **Chapter 12**: Real-world Analogies
* **Chapter 13**: Visual Learning
* **Chapter 14**: Story-based Learning
* **Chapter 15**: Code Explanation Rules
* **Chapter 16**: Adaptive Difficulty

### Book 4 — Learning Engine
* **Chapter 17**: Roadmap Generator
* **Chapter 18**: Prerequisite Detection
* **Chapter 19**: Knowledge Graph
* **Chapter 20**: Revision System
* **Chapter 21**: Confidence Tracking
* **Chapter 22**: Memory System

### Book 5 — Practical Learning
* **Chapter 23**: Tool Ecosystems
* **Chapter 24**: Free vs Paid Resources
* **Chapter 25**: Installation Guides
* **Chapter 26**: Mini Projects
* **Chapter 27**: Portfolio Projects
* **Chapter 28**: Debugging

### Book 6 — Career Engine
* **Chapter 29**: Resume Builder
* **Chapter 30**: ATS Optimization
* **Chapter 31**: LinkedIn
* **Chapter 32**: GitHub
* **Chapter 33**: Job Search
* **Chapter 34**: Fake Job Detection
* **Chapter 35**: Communities

### Book 7 — Interview Engine
* **Chapter 36**: Coding Interviews
* **Chapter 37**: Java Interviews
* **Chapter 38**: HR Interviews
* **Chapter 39**: Mock Interviews
* **Chapter 40**: Final Evaluation

### Book 8 — Graduation
* **Chapter 41**: Portfolio Review
* **Chapter 42**: Resume Review
* **Chapter 43**: Career Roadmap
* **Chapter 44**: Continuous Learning

---

## ⚙️ How to Adopt the AI-MOS Standard

AI-MOS is **AI-independent**. It is designed to work out of the box with models such as:
* **Anthropic Claude** (Sonnet/Opus)
* **OpenAI ChatGPT** (GPT-4o/o1/o3-mini)
* **Google Gemini** (1.5 Pro / 2.0 Flash)
* **DeepSeek-V3 / DeepSeek-R1**
* **Meta Llama 3** (70B/405B)

### Context Assembly Pattern
Systems implementing the AI-MOS standard should dynamically compile system prompts by referencing specific modules depending on the active state. For example:
1. **Intake Mode**: Compile prompts using Volume 2 (Student Discovery).
2. **Standard Socratic Lesson**: Compile prompts using Volume 1 (Foundations) + Volume 3 (Teaching Engine) + active node markdown text.
3. **Assessment Mode**: Compile prompts using Volume 1 + Volume 5 (Interview Engine).

---

## 🤝 How to Contribute

AI-MOS v2.0 is maintained as an open-source standard. We encourage developers, educators, and curriculum designers to help refine it:
1. Propose modifications to specific volume chapters.
2. Share Socratic prompting templates that successfully resolve tutorial hell.
3. Help extend standard templates to other languages (Python, Go, Rust) and career tracks.
