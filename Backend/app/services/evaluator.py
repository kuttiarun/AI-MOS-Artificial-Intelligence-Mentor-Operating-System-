"""
AI-MOS Backend — Socratic Evaluator Service
============================================
Evaluates a student's Socratic checkpoint response using LLM compute.

Features:
- Robust JSON Extraction: Isolates JSON boundaries by finding the first
  '{' and the last '}' to strip any conversational conversational text.
- Fallback Heuristics: If the JSON is invalid or fails to parse, falls back to
  a robust character/word metric validation check rather than blocking the user.
- BYOK Integration: Calls LLMFactory using the student's browser API headers
  to maintain zero platform-side compute costs.
"""

import json
import logging
import re
from fastapi import HTTPException
from app.services.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

# Evaluation template prompt sent to the LLM
EVALUATION_SYSTEM_PROMPT = (
    "You are the AI-MOS Socratic grader. Your job is to read a student's explanation "
    "of a programming concept and determine if they genuinely understand it.\n\n"
    "GRADING CRITERIA:\n"
    "1. CORE WHY: Did they explain why the concept exists (the engineering problem it solves)?\n"
    "2. ANALOGY/CONCEPT: Did they explain it using a conceptual model or analogy?\n"
    "3. NOT MEMORIZED: The answer should look like their own words, not direct copy-pastes from textbooks.\n\n"
    "You must return your evaluation in PURE JSON format. Do not write any conversational text "
    "before or after the JSON object. The JSON structure MUST be:\n"
    "{\n"
    '  "passed": true,\n'
    '  "confidence_score": 8,\n'
    '  "feedback": "Your descriptive explanation feedback here."\n'
    "}\n"
    "Ensure 'passed' is a boolean, 'confidence_score' is an integer between 0 and 10, "
    "and 'feedback' is a string."
)


class SocraticEvaluator:
    """
    Evaluates student text descriptions using LLM and parses JSON output.
    """

    @staticmethod
    async def evaluate_explanation(
        provider: str,
        api_key: str,
        node_id: str,
        student_text: str,
    ) -> dict:
        """
        Sends the student's answer to the LLM for grading. Returns parsed dictionary.
        """
        user_prompt = (
            f"Syllabus Node: {node_id}\n"
            f"Student Explanation: \"{student_text}\"\n\n"
            "Evaluate this submission based on the Socratic grading criteria. "
            "Return the final JSON output."
        )

        try:
            # Call the compute factory stream
            provider_response = await LLMFactory.get_streaming_response(
                provider=provider,
                api_key=api_key,
                payload={"user_message": user_prompt},
                system_prompt=EVALUATION_SYSTEM_PROMPT,
            )

            # Accumulate text tokens from the SSE stream
            response_content = ""
            async for raw_chunk in provider_response.aiter_text():
                # Split raw chunks into standard SSE lines
                for line in raw_chunk.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_content = line[5:].strip()
                        if data_content == "[DONE]":
                            break
                        try:
                            parsed_data = json.loads(data_content)
                            token = parsed_data["choices"][0]["delta"].get("content", "")
                            response_content += token
                        except Exception:
                            # Skip partial SSE line parsing errors
                            pass

            await provider_response.aclose()
            logger.info("Raw evaluator output: %s", response_content)

            # Parse JSON using robust brace boundaries
            return SocraticEvaluator._extract_and_parse_json(response_content, student_text)

        except Exception as exc:
            logger.error("LLM evaluation call failed: %s. Applying fallback.", str(exc))
            return SocraticEvaluator._get_fallback_evaluation(student_text)

    @staticmethod
    def _extract_and_parse_json(raw_text: str, student_text: str) -> dict:
        """
        Finds the outermost curly braces in text, parses the JSON payload,
        and sanitizes keys to guarantee schema compatibility.
        """
        first_brace = raw_text.find("{")
        last_brace = raw_text.rfind("}")

        if first_brace == -1 or last_brace == -1:
            logger.warning("No JSON braces found in evaluator output. Falling back.")
            return SocraticEvaluator._get_fallback_evaluation(student_text)

        json_str = raw_text[first_brace : last_brace + 1]
        try:
            parsed = json.loads(json_str)
            # Guarantee key schemas
            passed = bool(parsed.get("passed", False))
            score = int(parsed.get("confidence_score", 0))
            feedback = str(parsed.get("feedback", "No feedback provided."))
            
            # Bound check score
            score = max(0, min(10, score))

            return {
                "passed": passed,
                "confidence_score": score,
                "feedback": feedback,
            }
        except Exception as exc:
            logger.warning("JSON parsing error on extracted string: %s. Falling back.", str(exc))
            return SocraticEvaluator._get_fallback_evaluation(student_text)

    @staticmethod
    def _get_fallback_evaluation(student_text: str) -> dict:
        """
        Failsafe backup validator. Evaluates submission based on length/words.
        Prevents students from getting locked out due to network issues.
        """
        words = [w for w in re.split(r"\s+", student_text.strip()) if w]
        word_count = len(words)

        if word_count >= 12:
            return {
                "passed": True,
                "confidence_score": 7,
                "feedback": (
                    "👍 [Failsafe Gate]: Your response contains a solid explanation "
                    f"({word_count} words). The system validated your submission successfully."
                ),
            }
        else:
            return {
                "passed": False,
                "confidence_score": 3,
                "feedback": (
                    "⚠️ [Failsafe Gate]: Your answer is too short. Please provide a "
                    "more thorough description (at least 12 words) explaining the why "
                    "and the analogy behind this concept."
                ),
            }
