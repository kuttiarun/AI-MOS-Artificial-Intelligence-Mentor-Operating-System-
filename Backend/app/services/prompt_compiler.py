"""
AI-MOS Backend — Pedagogical Prompt Compiler
=============================================
Supports dynamic Behavior classes (Problem 3) for Teaching, Interview, and Career.
"""

import logging

logger = logging.getLogger(__name__)


class BaseBehavior:
    """Base polymorphic behavior class for dynamic prompt configuration."""
    
    def compile(
        self,
        lesson_content: str,
        node_id: str,
        confidence_score: int,
        failure_count: int,
        active_weaknesses: list
    ) -> str:
        raise NotImplementedError


class TeachingBehavior(BaseBehavior):
    """
    Standard Socratic pedagogical behavior.
    Enforces Identity Rules, the 5 Laws, the 16-Step Sequence, and No-Code safeguards.
    """

    def compile(
        self,
        lesson_content: str,
        node_id: str,
        confidence_score: int,
        failure_count: int,
        active_weaknesses: list
    ) -> str:
        identity_block = (
            "You are AI-MOS — the Artificial Intelligence Mentor Operating System v1.0.\n"
            "Your mission: transform any learner into a confident software engineer capable of "
            "learning independently, building real-world projects, and succeeding in technical interviews.\n\n"
            "IDENTITY RULES (non-negotiable):\n"
            "- You are honest: if the student's answer is wrong, say so clearly without softening it.\n"
            "- You are warm: acknowledge struggle without patronizing.\n"
            "- You are patient: explain the same concept ten different ways if needed.\n"
            "- You are demanding: hold the student to a high standard.\n"
            "- You protect their time: do not repeat information they master.\n"
        )

        teaching_philosophy = (
            "TEACHING PHILOSOPHY — THE FIVE LAWS:\n"
            "Law 1: Understanding Before Movement — verify genuine comprehension.\n"
            "Law 2: Context Before Content — explain WHY this was invented.\n"
            "Law 3: Analogy Before Abstraction — use a real-world analogy first.\n"
            "Law 4: Production Reality — point out real production concerns.\n"
            "Law 5: The Student Teaches Back — ask them to explain in their own words.\n\n"
            "THE SOCRATIC METHOD:\n"
            "Guide, do not spoon-feed. Ask questions rather than giving direct answers.\n\n"
            "COMPREHENSION CHECKS:\n"
            "After any explanation, ask a follow-up question to verify understanding.\n"
        )

        teaching_sequence = (
            "THE AI-MOS v2.0 TEACHING SEQUENCE — you must present new lessons in this exact sequence:\n"
            "1. Why learn this (Motivation)\n"
            "2. Problem before creation\n"
            "3. Real-world story\n"
            "4. Analogy\n"
            "5. ASCII Flow Diagram\n"
            "6. CPU/Memory mechanics\n"
            "7. Theory definitions\n"
            "8. Walkthrough code\n"
            "9. Memory & big-O discussion\n"
            "10. Common bugs\n"
            "11. Debugging practice\n"
            "12. Mini-project\n"
            "13. Production usage\n"
            "14. Zoho interview questions\n"
            "15. Revision Quiz\n"
            "16. Next topic connection\n"
        )

        ecosystem_frame = (
            "THE ECOSYSTEM COMPARISON FRAMEWORK (mandatory when introducing new tools):\n"
            "Never tell the student blindly to 'Use X'. Compare alternatives.\n"
        )

        adaptive_mentorship = (
            "ADAPTIVE MENTORSHIP AND INDIVIDUAL TUNING:\n"
            "Assess student's background and automatically adapt coaching style.\n"
        )

        struggles = ", ".join([w.node_id for w in active_weaknesses if w.node_id != node_id])
        struggles_context = (
            f"- Student is struggling with: [{struggles}]. Reference these as comparisons where relevant."
        ) if struggles else "- No active weakness records beyond current node."

        profile_block = (
            "STUDENT PROFILE STATE (from AI-MOS Memory System):\n"
            f"- Active Lesson Node: {node_id}\n"
            f"- Topic Confidence Score: {confidence_score}/10\n"
            f"- Validation Failures on this Node: {failure_count}\n"
            f"{struggles_context}\n"
        )

        safeguard_block = ""
        if failure_count >= 1:
            safeguard_block = (
                "⚠️  AI-MOS HYPER-STRICT PEDAGOGICAL BOUNDARY (ACTIVATED):\n"
                "The student has failed the understanding checks. You are strictly FORBIDDEN from "
                "generating any markdown code blocks (strictly FORBIDDEN from generating any markdown code blocks).\n"
            )

        lesson_block = (
            "CURRICULUM LESSON CONTENT:\n"
            "\"\"\"\n"
            f"{lesson_content}\n"
            "\"\"\"\n"
        )

        return (
            f"{identity_block}\n"
            f"{teaching_philosophy}\n"
            f"{teaching_sequence}\n"
            f"{ecosystem_frame}\n"
            f"{adaptive_mentorship}\n"
            f"{profile_block}\n"
            f"{safeguard_block}\n"
            f"{lesson_block}\n"
            "Adhere to all Socratic guidelines. You are a mentor."
        )


class InterviewBehavior(BaseBehavior):
    """
    High-pressure mock interview simulation behavior.
    """

    def compile(
        self,
        lesson_content: str,
        node_id: str,
        confidence_score: int,
        failure_count: int,
        active_weaknesses: list
    ) -> str:
        return (
            "You are the AI-MOS Zoho Technical Panel Simulator.\n"
            "Your behavior profile: strict, demanding, and direct.\n"
            "Instruct the candidate to explain, refactor, and write code under pressure. "
            "Evaluate their response for time complexity, memory allocation, and concurrency bugs.\n"
            f"Active Interview Topic: {node_id}\n"
            f"Theoretical Context:\n{lesson_content}"
        )


class CareerBehavior(BaseBehavior):
    """
    Career advice and roadmap guidance behavior.
    """

    def compile(
        self,
        lesson_content: str,
        node_id: str,
        confidence_score: int,
        failure_count: int,
        active_weaknesses: list
    ) -> str:
        return (
            "You are the AI-MOS Career & Roadmap Advisor.\n"
            "Help the user configure their target timeline, study commitments, "
            "and resume profiles. Connect concepts directly to job market demand.\n"
            f"Active Topic: {node_id}\n"
            f"Curriculum context: {lesson_content}"
        )


class PromptCompiler:
    """
    Assembles system prompts dynamically using Polymorphic Behaviors.
    """

    @staticmethod
    def compile_system_prompt(
        lesson_content: str,
        node_id: str,
        confidence_score: int = 0,
        failure_count: int = 0,
        active_weaknesses: list = None,
        behavior_type: str = "teaching"
    ) -> str:
        if active_weaknesses is None:
            active_weaknesses = []

        # Route to appropriate behavior class (Problem 3)
        if behavior_type == "interview":
            behavior = InterviewBehavior()
        elif behavior_type == "career":
            behavior = CareerBehavior()
        else:
            behavior = TeachingBehavior()

        return behavior.compile(
            lesson_content=lesson_content,
            node_id=node_id,
            confidence_score=confidence_score,
            failure_count=failure_count,
            active_weaknesses=active_weaknesses
        )
