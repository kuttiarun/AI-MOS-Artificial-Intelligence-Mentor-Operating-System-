"""
AI-MOS Backend — Pedagogical Prompt Compiler
=============================================
Algorithmic Socratic prompt engine that aggregates DB profile state
and curriculum texts to build customized, dynamic system instructions.

Design principles (PRD MOD-05 & SRS §1):
- Context-Awareness: Inject student's active weaknesses and current
  confidence into the LLM system prompt.
- Socratic Core: Enforce Socratic methodology on the model.
- "Research Coach" Anti-Laziness Guard: If failure_count >= 1 for the current
  concept, inject a strict boundary instruction completely forbidding any
  markdown code blocks (```java ... ```), forcing Socratic guidance and
  structural pseudocode only.
"""

import logging

logger = logging.getLogger(__name__)


class PromptCompiler:
    """
    Assembles structural system prompts by merging pedagogical rules,
    curriculum node texts, and student progress/weakness metrics.
    """

    @staticmethod
    def compile_system_prompt(
        lesson_content: str,
        node_id: str,
        confidence_score: int = 0,
        failure_count: int = 0,
        active_weaknesses: list = None,
    ) -> str:
        """
        Builds the fully aggregation prompt.

        Args:
            lesson_content:    Raw Markdown content of the current node.
            node_id:           Slug identifier of the active lesson.
            confidence_score:  User's current confidence score (0-10) for this node.
            failure_count:     Number of validation failures on this specific node.
            active_weaknesses: List of other active node IDs the user is struggling with.

        Returns:
            The compiled system instructions string.
        """
        if active_weaknesses is None:
            active_weaknesses = []

        # ---------------------------------------------------------------------
        # 1. Base Socratic Instructions (MOD-05 Core)
        # ---------------------------------------------------------------------
        base_socratic = (
            "You are the AI-MOS software engineering mentor. Your mission is to "
            "transform beginners into independent, first-principles-thinking engineers.\n"
            "Adopt a Socratic coaching style: guide, do not feed. Explain the 'why' "
            "before the 'how' using real-world analogies.\n\n"
            "CORE INSTRUCTIONS:\n"
            "- Always explain concepts using stories, real-world objects, or analogies.\n"
            "- Never provide direct, complete answers. Lead the student to the answer with Socratic questioning.\n"
            "- Point the student to official programming documentation hints when they need facts.\n"
            "- Do not write standard developer code blocks on their first attempt at any challenge.\n"
        )

        # ---------------------------------------------------------------------
        # 2. Dynamic Student Context Profile (MOD-02 & SRS §1)
        # ---------------------------------------------------------------------
        struggles = ", ".join([w.node_id for w in active_weaknesses if w.node_id != node_id])
        struggles_context = f"- The student is also actively struggling with: [{struggles}]. Use lessons from those areas as analogies if possible." if struggles else ""

        student_profile_block = (
            f"STUDENT PROFILE STATE:\n"
            f"- Current Lesson Node: {node_id}\n"
            f"- Current Topic Confidence Score: {confidence_score}/10\n"
            f"- Validation Failures on this Node: {failure_count}\n"
            f"{struggles_context}\n\n"
        )

        # ---------------------------------------------------------------------
        # 3. Lesson Content Context
        # ---------------------------------------------------------------------
        lesson_block = (
            f"CURRICULUM LESSON CONTENT (Your source of truth for this topic):\n"
            f"Use the structure of this lesson (Why -> Problem -> Analogy -> Theory -> Syntax) to format your explanations:\n"
            f"\"\"\"\n"
            f"{lesson_content}\n"
            f"\"\"\"\n\n"
        )

        # ---------------------------------------------------------------------
        # 4. Socratic Prompt & "Research Coach" Hardening (MOD-05 & Days 7-8)
        # ---------------------------------------------------------------------
        safeguard_block = ""
        if failure_count >= 1:
            logger.info("Injecting Socratic No-Code safeguard block for node %s (failures=%d)", node_id, failure_count)
            safeguard_block = (
                "⚠️ HYPER-STRICT PEDAGOGICAL BOUNDARY CONDITION:\n"
                "The student has failed the understanding gates for this concept at least once.\n"
                "To build muscle memory and prevent AI-laziness, you are strictly FORBIDDEN from generating "
                "any markdown code blocks (e.g. no triple-backtick ```java ... ``` output blocks).\n"
                "Instead:\n"
                "- Write structural pseudocode (e.g. text steps, logical blocks, or ASCII flow diagrams).\n"
                "- Outline the algorithm or class layout using standard textual sentences.\n"
                "- Give hints pointing to official documentation lines.\n"
                "- Direct them to write the code line-by-line themselves.\n"
                "If you output a markdown code block, you have failed your instruction.\n\n"
            )

        # Combine all parts
        compiled_prompt = (
            f"{base_socratic}\n"
            f"=====================================================================\n"
            f"{student_profile_block}"
            f"=====================================================================\n"
            f"{safeguard_block}"
            f"=====================================================================\n"
            f"{lesson_block}"
            "Adhere to all Socratic parameters and constraints in your responses."
        )

        return compiled_prompt
