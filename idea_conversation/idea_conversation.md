I gonna prepare for zoho interview for the java developer role, so I just want to learn all the requirements for the interview and I need a proper prompt for my interview preparation and I'm gonna implement the prompt in claude 

For a Java Developer role at Zoho Corporation, preparation should focus on problem-solving first, then Java fundamentals, OOP, collections, multithreading, SQL, DBMS, operating systems, networking basics, and machine coding.

What Zoho Usually Tests
1. Programming & Problem Solving (Highest Priority)

Expect coding questions involving:

Arrays
Strings
Matrix problems
Recursion
Pattern printing
Searching & Sorting
Hashing
Linked Lists
Stacks & Queues
Trees
Dynamic Programming (basic to medium)
Time Complexity analysis

Examples:

Longest substring without repeating characters
Rotate matrix
Remove duplicates
Anagram detection
LRU Cache
Balanced brackets
N-Queens
Sudoku validation
2. Core Java

Must know deeply:

JVM, JDK, JRE
Class & Objects
Constructors
Inheritance
Polymorphism
Abstraction
Encapsulation
Method Overloading vs Overriding
Interface vs Abstract Class
Access Modifiers
Static Keyword
Final Keyword
Exception Handling
Garbage Collection
String, StringBuilder, StringBuffer
Wrapper Classes
Generics
3. Java Collections Framework

Very important.

Know:

ArrayList
LinkedList
HashMap
LinkedHashMap
TreeMap
HashSet
TreeSet
PriorityQueue
Comparable
Comparator

Interview questions:

HashMap internal working
HashSet implementation
Hash collision handling
Difference between ArrayList and LinkedList
TreeMap vs HashMap
4. Multithreading

Understand:

Thread creation
Runnable
Thread lifecycle
Synchronization
Deadlock
Race Condition
Executor Framework
Callable & Future
Concurrent Collections
5. SQL & DBMS

Must know:

Joins
Group By
Having
Subqueries
Normalization
Indexing
Transactions
ACID Properties

Practice writing queries manually.

6. Operating Systems
Process vs Thread
Scheduling
Deadlock
Paging
Virtual Memory
Context Switching
7. Computer Networks
HTTP vs HTTPS
TCP vs UDP
DNS
REST APIs
Cookies & Sessions
8. Low-Level Design / Mini Project Discussion

Be prepared to design:

Library Management System
Parking Lot
ATM
Movie Ticket Booking
Online Shopping System

Using OOP principles.

Master Prompt for Claude

Copy this entire prompt into Claude:

Act as a Senior Zoho Interviewer with 15+ years of experience hiring Java Developers.

Your task is to prepare me for a Zoho Java Developer interview from beginner to advanced level.

Follow these strict rules:

1. Create a complete preparation roadmap.

2. Divide preparation into phases:

Phase 1:
Programming Logic and Problem Solving

Phase 2:
Core Java

Phase 3:
Object Oriented Programming

Phase 4:
Collections Framework

Phase 5:
Exception Handling

Phase 6:
Multithreading and Concurrency

Phase 7:
JVM Internals and Garbage Collection

Phase 8:
SQL and DBMS

Phase 9:
Operating Systems

Phase 10:
Computer Networks

Phase 11:
Low Level Design

Phase 12:
Behavioral and HR Round

3. Teach each topic using:
- Theory
- Real-world examples
- Visual explanations
- Common interview questions
- Common mistakes
- Memory tricks
- Zoho-specific expectations

4. After teaching a topic:
- Ask interview questions
- Wait for my answer
- Evaluate my answer
- Explain weaknesses
- Give an improved answer

5. For coding problems:
- Start easy
- Move to medium
- Move to Zoho-level hard questions

For every coding question provide:
- Problem statement
- Clarification questions
- Brute force approach
- Optimized approach
- Time complexity
- Space complexity
- Java implementation
- Alternative solutions

6. Conduct mock interviews exactly like a real Zoho interviewer.

Rules:
- Ask one question at a time.
- Do not reveal answers immediately.
- Challenge weak answers.
- Ask follow-up questions.
- Score every answer out of 10.
- Maintain interview pressure similar to Zoho.

7. Create a daily preparation plan for:
- 7 days
- 15 days
- 30 days

8. Identify weak areas automatically based on my answers and generate revision plans.

9. Assume I am preparing specifically for a Java Developer role and optimize preparation accordingly.

10. Begin by assessing my current level through a detailed diagnostic interview and then create a personalized roadmap.
Additional Prompt (Mock Interview Mode)
Act as a Zoho Senior Java Interview Panel.

Conduct a complete interview.

Rules:
- One question at a time.
- Start from introductions.
- Ask Java, OOP, Collections, Multithreading, SQL, OS, Networks and Coding questions.
- Do not give answers until I answer.
- Ask follow-up questions.
- Evaluate communication skills.
- Evaluate technical depth.
- Evaluate confidence.
- Give detailed feedback after each answer.
- Simulate actual interview pressure.
- End with a final hiring recommendation.

If the interview is within the next 1–2 weeks, spend roughly:

40% on DSA/problem solving
25% on Core Java + Collections
15% on SQL/DBMS
10% on OS + Networks
10% on mock interviews and project discussions

This distribution aligns well with what Java-focused product companies such as Zoho commonly emphasize.

Your idea is ambitious and technically feasible, but there's an important design choice to make before writing a prompt for another coding agent.

What you've described is not a website. It's an AI-powered education platform with:

A curriculum engine
A learning-state engine
A RAG knowledge base
AI model orchestration
Career guidance
Progress tracking
Interview simulation
Resume optimization
Project management

A single prompt asking an AI to "build all of this" will almost certainly produce an unmaintainable project. A better approach is to have the AI first design the architecture, then implement it module by module with clear specifications.

I also can't honestly give you a "perfect prompt" that claims to completely specify a system of this size in one message. A project like this needs a proper Software Requirements Specification (SRS), architecture document, API design, database schema, UI/UX specification, and development roadmap.

What I recommend instead

Treat AI-MOS like a startup product.

Create these documents first:

Vision & Mission
Product Requirements Document (PRD)
Software Requirements Specification (SRS)
System Architecture
Database Design
UI/UX Design System
API Specification
AI Orchestration Specification
Knowledge Base Specification
Development Roadmap
Testing Strategy
Deployment & Scaling Plan

Then use Antigravity (or any coding AI) to implement one milestone at a time.

Product Vision (starting point)

Project Name

AI-MOS (Artificial Intelligence Mentor Operating System)

Mission

Build the world's most comprehensive AI-powered software engineering mentor that transforms complete beginners into industry-ready engineers through personalized learning, real-world projects, adaptive teaching, continuous assessment, and career guidance.

Core Philosophy

AI-MOS should not behave like a chatbot.

It should behave like:

A senior software engineer
A mentor
A teacher
A career coach
A technical interviewer
A project lead
A learning psychologist

Its objective is not to answer questions but to produce independent engineers who can continue learning without depending on AI.

Product Principles

The system should always:

Teach from first principles.
Never assume prior knowledge.
Explain the "why" before the "how."
Prefer intuition before syntax.
Adapt to the learner's level and pace.
Prioritize free and open-source resources when appropriate.
Compare ecosystems before recommending technologies.
Encourage independent research and critical thinking.
Track progress, confidence, and recurring mistakes.
Prevent learners from skipping essential prerequisites.
High-Level Modules
Authentication & User Profiles
Career Discovery
Diagnostic Assessment
Learning Engine
Knowledge Base / RAG
AI Orchestrator (Claude, ChatGPT, Gemini, etc.)
Progress Tracking
Project Builder
Resume & Portfolio
Interview Simulator
Job Search Assistant
Admin / Content Management
AI Orchestrator

The AI model should not contain all logic.

Instead:

The platform stores:
Teaching rules
Curriculum
User progress
Knowledge base
The backend retrieves only the relevant information.
The selected LLM receives:
Current lesson
User profile
Teaching rules
Context
The LLM generates the response.

This keeps prompts manageable and makes the platform model-agnostic.

Technology Stack (one example)

Frontend:

React
TypeScript
Tailwind CSS
React Router

Backend:

FastAPI (Python)

Database:

PostgreSQL

Cache:

Redis

Vector Database:

Qdrant or pgvector

Authentication:

JWT / OAuth

Storage:

S3-compatible storage

AI Providers:

OpenAI
Anthropic
Google
OpenRouter (optional)

Search:

Hybrid keyword + vector retrieval
Development Strategy

Don't ask Antigravity to build everything at once.

Break it into milestones, for example:

User authentication and profiles
Career discovery wizard
Diagnostic assessment
Learning dashboard
Knowledge base
AI orchestration
Progress tracking
Resume builder
Mock interviews
Job search features

Each milestone should be independently testable.

One additional recommendation

Since you're interested in building a serious platform, I'd also include:

A plugin architecture so new learning modules can be added without changing the core system.
Versioned curricula so content can evolve over time.
Analytics to measure which explanations help learners most.
Human mentor support in the future.
A content review workflow so educational material can be updated and validated.
My strongest recommendation

Before writing any code, write the PRD and SRS. Those two documents will define the product much more clearly than any single prompt. Once those are complete, an AI coding assistant like Antigravity can generate code far more reliably because it has a stable specification to implement.

ok do as you wish

I actually think we should go one step further.

Based on everything we've discussed, I don't want to create just another AI tutor. I want to design something that could become an actual product.

My Proposal

Instead of writing prompts first, let's build this like a startup.

Project Name:

AI-MOS (Artificial Intelligence Mentor Operating System)

Tagline:

Learn. Build. Think. Grow.

Mission:

To create the world's most intelligent software engineering mentor that doesn't just answer questions, but transforms beginners into independent engineers through adaptive teaching, practical experience, career guidance, and continuous mentorship.

Phase 1 (Most Important)

Before Antigravity writes a single line of code,

we should create

AI-MOS Blueprint

This becomes the constitution of the whole platform.

It contains

Vision
Mission
Goals
User Types
Teaching Philosophy
System Architecture
UI Principles
AI Principles
Career Principles
Learning Principles
Engineering Principles

This document never changes much.

Phase 2

Product Requirements Document (PRD)

This answers

What exactly are we building?

Example

Dashboard

↓

Learning Engine

↓

AI Mentor

↓

Career Assistant

↓

Resume Builder

↓

Mock Interview

↓

Projects

↓

Job Search

↓

Analytics
Phase 3

Software Requirements Specification (SRS)

Now we become engineers.

Everything becomes measurable.

Example

Authentication

Functional Requirements

Non-functional Requirements

API

Database

Security

Error Handling

Performance

Scalability

Logging

Caching

Everything.

Phase 4

System Design

This is where most people start.

We won't.

We start after understanding the product.

Example

React

↓

FastAPI

↓

PostgreSQL

↓

Redis

↓

Vector DB

↓

AI Gateway

↓

Claude

↓

OpenAI

↓

Gemini
Phase 5

Knowledge Engine

This is where your original idea becomes powerful.

Instead of one huge prompt...

Imagine this:

knowledge/

java/

dsa/

git/

github/

docker/

linux/

sql/

os/

network/

projects/

resume/

linkedin/

career/

behavioral/

communication/

Each topic is stored separately.

Example

git/

Introduction.md

History.md

First Principles.md

Installation.md

Windows.md

Ubuntu.md

Mac.md

Commands.md

Projects.md

Interview.md

Resources.md

Debugging.md

Comparison.md

Now Claude doesn't receive

100 pages.

It only receives

Git.

Phase 6

Teaching Engine

This is the heart.

Every lesson follows one standard.

WHY

↓

Problem

↓

Story

↓

Analogy

↓

Visualization

↓

Theory

↓

Syntax

↓

Code

↓

Debugging

↓

Mini Project

↓

Interview

↓

Revision

↓

Next Topic

Exactly like you wanted.

Phase 7

Career Engine

This is unique.

Instead of asking

What role?

AI first teaches

Software Industry.

For every role it explains

What they do
Salary
Daily work
Tech stack
IDEs
Languages
Career growth
Companies
Projects
Learning roadmap
Future opportunities
AI impact

Then asks

Now which role interests you?

Phase 8

Research Engine

I loved your idea about making learners independent.

So AI-MOS should teach

How to Google effectively.

How to read documentation.

How to compare AI answers.

How to verify information.

How to debug.

How to ask better questions.

How to learn independently.

Eventually,

students shouldn't need AI-MOS every day.

That is success.

Phase 9

Learning Memory

Every student gets

Profile

↓

Resume

↓

Current Topic

↓

Completed Lessons

↓

Weak Areas

↓

Projects

↓

GitHub

↓

LinkedIn

↓

Interview Scores

↓

Learning Style

↓

Preferred Language

↓

OS

↓

Budget

↓

Hardware

↓

Confidence

↓

Research Skills

↓

Communication

Everything stays updated.

Phase 10

The AI Gateway

This is where your website becomes different.

Instead of connecting directly to Claude,

create

AI Gateway

The gateway decides

Need reasoning?

↓

Claude

Need coding?

↓

GPT

Need images?

↓

Gemini

Need summarization?

↓

Another model

Later,

you can let users choose.

Phase 11

Future Marketplace

Imagine

Community

↓

Teachers

↓

Open Source Lessons

↓

Projects

↓

Templates

↓

Career Roadmaps

↓

Mock Interviews

↓

Study Groups

Others can contribute.

Phase 12

The Long-Term Vision

I wouldn't market AI-MOS as

"An AI Tutor"

I would market it as

"The Operating System for Learning Software Engineering."

The part I would tell Antigravity

If I were writing the instruction for Antigravity, I would not ask it to generate code immediately. I would say:

You are the Chief Software Architect for AI-MOS. Your responsibility is to help design and build a production-grade AI-powered education platform that prioritizes learning quality, maintainability, scalability, and extensibility over rapid feature development. Never jump directly to implementation. For every major feature, first produce the architecture, explain design trade-offs, identify risks, define APIs and database changes, and wait for approval before writing production code. Every module must be modular, testable, well-documented, and independently deployable where appropriate. Build AI-MOS as if it will eventually serve millions of learners worldwide.

What I think we should build together

Rather than creating a long prompt, we should create a complete open-source project with:

A detailed Product Requirements Document (PRD)
A Software Requirements Specification (SRS)
System architecture diagrams
Database schema
API contracts
UI/UX specifications
Teaching methodology documents
Knowledge base structure
Development roadmap
Coding standards
Testing strategy
Deployment guide

That would give Antigravity (or any development team) a clear blueprint to build from instead of relying on a single oversized prompt. It also makes AI-MOS maintainable, extensible, and much more likely to succeed as a real product.

ok where do we start first and do it

I think we should build this exactly like successful products such as Notion, Linear, or GitHub are built—not by writing code first, but by defining the product.

If we skip this stage, we'll eventually rewrite large parts of the system because new ideas will keep emerging.

The order I recommend
Step 1  Vision Document
        ↓
Step 2  Product Requirements Document (PRD)
        ↓
Step 3  Software Requirements Specification (SRS)
        ↓
Step 4  UI/UX Design
        ↓
Step 5  Database Design
        ↓
Step 6  System Architecture
        ↓
Step 7  Development Roadmap
        ↓
Step 8  Build MVP
        ↓
Step 9  Testing
        ↓
Step 10 Launch
We start with Step 1
AI-MOS Vision Document v1.0

This is the most important document.

If this document is clear, every future decision becomes easier.

1. Project Information

Project Name

AI-MOS

Artificial Intelligence Mentor Operating System

Tagline

Learn. Build. Think. Grow.

Project Type

AI-powered Software Engineering Education Platform

2. Mission

AI-MOS exists to transform complete beginners into confident software engineers by combining adaptive AI mentoring, project-based learning, real-world explanations, career guidance, and continuous assessment.

Unlike traditional AI chatbots that simply answer questions, AI-MOS acts as a long-term mentor, guiding learners from their first line of code to becoming industry-ready professionals capable of learning independently.

3. Vision

Become the world's most trusted AI mentor for software engineering education by providing personalized, structured, and practical learning experiences that emphasize understanding over memorization.

The long-term goal is to make high-quality software engineering education accessible to anyone with an internet connection, regardless of background, language, or financial constraints.

4. Core Problem

Today's learners face several challenges:

Information is scattered across countless websites and courses.
Many tutorials teach syntax without explaining why concepts exist.
AI often gives direct answers without ensuring genuine understanding.
Learners struggle to choose the right career path.
Interview preparation is disconnected from practical development.
Resume building, portfolio creation, and job searching are treated as separate activities.
Many learners become dependent on AI instead of developing research and problem-solving skills.
Existing platforms rarely adapt to the learner's pace or knowledge gaps.
5. Our Solution

AI-MOS integrates all essential aspects of becoming a software engineer into one platform.

The platform will:

Assess the learner's current skills.
Recommend suitable career paths.
Build personalized learning roadmaps.
Teach from first principles.
Explain concepts using real-world analogies.
Encourage independent research.
Build progressively larger projects.
Track knowledge and confidence.
Optimize resumes and portfolios.
Conduct mock interviews.
Guide job applications.
Continue mentoring throughout the learner's career.
6. Primary Goals
Teach understanding, not memorization.
Build independent learners.
Provide adaptive learning paths.
Connect theory to real-world engineering.
Prepare learners for interviews and professional work.
Keep education affordable by prioritizing free resources.
Support multiple AI providers.
Maintain a modular, extensible architecture.
7. Non-Goals

To keep the product focused, AI-MOS will not aim to:

Replace human mentors entirely.
Guarantee job placement.
Cover every academic discipline.
Encourage shortcut learning or cheating.
Hide uncertainty when information is incomplete.
8. Guiding Principles
Teach from first principles.
Explain the "why" before the "how."
Prefer simple language over technical jargon.
Use stories, analogies, and real-world examples.
Verify understanding before progressing.
Adapt to each learner.
Encourage critical thinking.
Prefer free and open-source resources when appropriate.
Present ecosystems before recommending tools.
Continuously update learner progress.
9. Success Metrics

The platform succeeds when learners:

Understand concepts deeply.
Can explain concepts in their own words.
Build complete projects.
Debug independently.
Read documentation confidently.
Research effectively.
Perform well in interviews.
Maintain professional portfolios.
Continue learning new technologies without relying heavily on AI.
10. Target Audience

Primary:

Beginners
College students
Career changers
Self-taught developers

Secondary:

Experienced engineers learning new technologies
Professionals switching domains
Companies onboarding junior developers
11. Long-Term Vision

AI-MOS should evolve beyond a learning platform into a lifelong engineering companion that supports learners throughout their careers, from their first programming lesson to senior engineering responsibilities.

What comes next?

Once this Vision Document is stable, the next document will be the Product Requirements Document (PRD).

The PRD answers:

What features will the platform have?
What problems does each feature solve?
Who uses each feature?
What does the user experience look like?
What is included in the first release versus later versions?

That PRD becomes the foundation for the software architecture and implementation.

One recommendation before we continue

Since this is a substantial project with the potential to become open source or even a startup, we should keep everything in a version-controlled repository from day one. A structure like this would work well:

AI-MOS/
├── docs/
│   ├── vision.md
│   ├── prd.md
│   ├── srs.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── api/
│   ├── database/
│   └── ui/
├── backend/
├── frontend/
├── knowledge-base/
├── prompts/
├── tests/
└── README.md

That way, every design decision is documented before implementation begins, making it much easier to collaborate, evolve the platform, and eventually build a production-quality system.