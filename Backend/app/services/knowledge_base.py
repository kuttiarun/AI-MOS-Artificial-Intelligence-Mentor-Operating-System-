"""
AI-MOS Backend — Markdown Knowledge Base Service
=================================================
Provides asynchronous reading and caching for localized curriculum
Markdown files stored under the root `curriculum/` directory.

Design principles:
- Asynchronous File I/O: Uses anyio.to_thread.run_sync to offload blocking
  file reads from the FastAPI main event loop.
- In-Memory Caching: Stores loaded markdown content in a dictionary cache.
  If a lesson is requested multiple times, it is served instantly without
  hitting the disk.
- Robust Path Resolution: Resolves paths relative to the project root's
  `curriculum/` folder, preventing directory traversal attacks.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import anyio
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Service layer responsible for fetching, caching, and serving
    the markdown lesson contents.
    """
    # Simple thread-safe in-memory cache mapping content_path to content string
    _cache: Dict[str, str] = {}

    # Root directory for curriculum files (d:/AI-MOS Project/curriculum)
    # Resolved relative to this file: parents[3]
    CURRICULUM_ROOT: Path = Path(__file__).resolve().parents[3] / "curriculum"

    @classmethod
    async def get_lesson_content(cls, content_path: str) -> str:
        """
        Reads and returns the content of the markdown file at `content_path`.
        Caches the file contents in memory.

        Args:
            content_path: Relative path stored in DB (e.g. 'phase-3/04-hashmap.md'
                          or 'curriculum/phase-3/04-hashmap.md')

        Returns:
            The raw Markdown text contents.

        Raises:
            HTTPException 404: File not found or path lies outside root.
        """
        # Clean the input path
        # If the DB stored 'curriculum/phase-3/04-hashmap.md', strip the leading 'curriculum/'
        cleaned_path = content_path.strip().lstrip("/")
        if cleaned_path.startswith("curriculum/"):
            cleaned_path = cleaned_path[len("curriculum/"):]

        # Check in-memory cache first
        if cleaned_path in cls._cache:
            logger.debug("Cache hit for curriculum file: %s", cleaned_path)
            return cls._cache[cleaned_path]

        # Resolve the full path on disk
        full_path = (cls.CURRICULUM_ROOT / cleaned_path).resolve()

        # Prevent Directory Traversal vulnerability
        try:
            # Check if resolved path is indeed inside CURRICULUM_ROOT
            full_path.relative_to(cls.CURRICULUM_ROOT.resolve())
        except ValueError as exc:
            logger.error("Directory traversal attempt blocked: %s", content_path)
            raise HTTPException(
                status_code=404,
                detail="The requested curriculum resource could not be found."
            ) from exc

        if not full_path.is_file():
            logger.warning("Curriculum file not found on disk: %s", full_path)
            raise HTTPException(
                status_code=404,
                detail=f"Lesson content file '{cleaned_path}' was not found on the server."
            )

        # Read the file asynchronously using thread offloading
        try:
            content = await anyio.to_thread.run_sync(cls._read_file_sync, full_path)
            # Store in cache
            cls._cache[cleaned_path] = content
            logger.info("Successfully loaded and cached curriculum node: %s", cleaned_path)
            return content
        except Exception as exc:
            logger.error("Failed to read curriculum file: %s (%s)", full_path, str(exc))
            raise HTTPException(
                status_code=500,
                detail="An error occurred while reading the lesson content from disk."
            ) from exc

    @staticmethod
    def _read_file_sync(file_path: Path) -> str:
        """Synchronous file-reading block run in the thread pool."""
        return file_path.read_text(encoding="utf-8")

    @classmethod
    def clear_cache(cls) -> None:
        """Clears the in-memory cache (useful for dev and testing)."""
        cls._cache.clear()
        logger.info("Curriculum knowledge cache cleared.")
