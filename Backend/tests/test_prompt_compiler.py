"""
AI-MOS Backend — Prompt Compiler & Socratic Engine Unit Tests
=============================================================
Tests prompt aggregation logic, Socratic injection rules, and Socratic
No-Code restrictions.
"""

from app.services.prompt_compiler import PromptCompiler


def test_base_socratic_prompt_structure():
    """
    Verifies that the compiled system prompt contains the base Socratic
    parameters and the loaded lesson content.
    """
    lesson_content = "This is a lesson about Polymorphism in Java."
    node_id = "java-oop-polymorphism"

    compiled = PromptCompiler.compile_system_prompt(
        lesson_content=lesson_content,
        node_id=node_id,
        confidence_score=5,
        failure_count=0,
        active_weaknesses=[],
    )

    # Assert base Socratic guidelines are present
    assert "You are AI-MOS — the Artificial Intelligence Mentor Operating System v1.0." in compiled
    assert "THE SOCRATIC METHOD" in compiled
    assert "COMPREHENSION CHECKS" in compiled

    # Assert lesson text is present
    assert "This is a lesson about Polymorphism in Java." in compiled

    # Assert student context details are present
    assert f"Active Lesson Node: {node_id}" in compiled
    assert "Topic Confidence Score: 5/10" in compiled
    assert "Validation Failures on this Node: 0" in compiled


def test_no_code_safeguard_triggers_on_failures():
    """
    Verifies that the strict pedagogical boundary condition (banning code blocks)
    is injected ONLY when the failure count is >= 1.
    """
    lesson_content = "This is a lesson about Polymorphism."
    node_id = "java-oop-polymorphism"

    # Case A: 0 failures -> No-Code boundary should NOT be in prompt
    compiled_no_failures = PromptCompiler.compile_system_prompt(
        lesson_content=lesson_content,
        node_id=node_id,
        failure_count=0,
    )
    assert "AI-MOS HYPER-STRICT PEDAGOGICAL BOUNDARY" not in compiled_no_failures
    assert "strictly FORBIDDEN from generating any markdown code blocks" not in compiled_no_failures

    # Case B: 1 failure -> No-Code boundary MUST be injected
    compiled_one_failure = PromptCompiler.compile_system_prompt(
        lesson_content=lesson_content,
        node_id=node_id,
        failure_count=1,
    )
    assert "AI-MOS HYPER-STRICT PEDAGOGICAL BOUNDARY" in compiled_one_failure
    assert "strictly FORBIDDEN from generating any markdown code blocks" in compiled_one_failure

    # Case C: 3 failures -> No-Code boundary MUST be injected
    compiled_multiple_failures = PromptCompiler.compile_system_prompt(
        lesson_content=lesson_content,
        node_id=node_id,
        failure_count=3,
    )
    assert "AI-MOS HYPER-STRICT PEDAGOGICAL BOUNDARY" in compiled_multiple_failures

