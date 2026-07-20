import logging
from uuid import UUID
from typing import AsyncGenerator
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.knowledge_base import KnowledgeBaseService
from app.services.prompt_compiler import PromptCompiler
from app.services.llm_factory import LLMFactory
from app.services.progress import (
    get_user_node_progress,
    get_node_weakness,
    get_active_weak_areas,
    get_curriculum_node,
)

logger = logging.getLogger(__name__)

class AimosKernel:
    """
    AI-MOS Kernel (CTO Review - Problem 2)
    Acts as the centralized orchestrator managing User Context, Learning State,
    Knowledge Retrieval, and AI Gateway interactions.
    """

    @staticmethod
    async def load_learning_state(db: AsyncSession, user_uuid: UUID, node_id: str) -> dict:
        """
        Loads the active user context, failures, confidence, and weaknesses.
        """
        progress = await get_user_node_progress(db, user_uuid, node_id)
        confidence = progress.confidence_score if progress else 0

        weakness = await get_node_weakness(db, user_uuid, node_id)
        failures = weakness.failure_count if weakness else 0

        all_weaknesses = await get_active_weak_areas(db, user_uuid)

        return {
            "confidence_score": confidence,
            "failure_count": failures,
            "active_weaknesses": all_weaknesses
        }

    @staticmethod
    async def retrieve_knowledge(node_id: str, db: AsyncSession) -> tuple[str, str]:
        """
        Fetches the curriculum metadata and markdown content.
        """
        node = await get_curriculum_node(db, node_id)
        if not node:
            raise HTTPException(
                status_code=404,
                detail=f"Curriculum node '{node_id}' does not exist."
            )
        lesson_content = await KnowledgeBaseService.get_lesson_content(node.content_path)
        return node.title, lesson_content

    @staticmethod
    async def stream_socratic_chat(
        db: AsyncSession,
        user_uuid: UUID,
        node_id: str,
        payload: dict,
        provider: str,
        api_key: str,
        behavior_type: str = "teaching"
    ) -> AsyncGenerator[str, None]:
        """
        Orchestrates Socratic AI streams through the AI-MOS Kernel.
        """
        # 1. Retrieve knowledge content
        _, lesson_content = await AimosKernel.retrieve_knowledge(node_id, db)

        # 2. Retrieve user context & learning state
        state = await AimosKernel.load_learning_state(db, user_uuid, node_id)

        # 3. Dynamic Prompting via Behaviors compiler
        system_prompt = PromptCompiler.compile_system_prompt(
            lesson_content=lesson_content,
            node_id=node_id,
            confidence_score=state["confidence_score"],
            failure_count=state["failure_count"],
            active_weaknesses=state["active_weaknesses"],
            behavior_type=behavior_type
        )

        # 4. Stream response from compute adapters
        event_stream = await LLMFactory.get_streaming_response(
            provider=provider,
            api_key=api_key,
            payload=payload,
            system_prompt=system_prompt,
        )

        async for chunk in event_stream:
            if chunk:
                yield chunk
