"""
AI-MOS Backend — Knowledge Base Service Unit Tests
===================================================
Verifies async file loading, relative resolving, directory traversal
prevention, and caching operations of the KnowledgeBaseService.
"""

import pytest
from fastapi import HTTPException
from app.services.knowledge_base import KnowledgeBaseService


@pytest.mark.asyncio
async def test_successful_lesson_loading_and_caching():
    """
    Verifies that the knowledge engine successfully loads a valid lesson file
    and stores it in the cache for subsequent hits.
    """
    # Clean the cache first to ensure test isolation
    KnowledgeBaseService.clear_cache()

    path = "phase-3/04-hashmap.md"

    # 1. Fetch content from disk
    content = await KnowledgeBaseService.get_lesson_content(path)
    assert "# HashMap: Hashing, Buckets, and Collision Resolution" in content
    assert "Core Why" in content

    # 2. Check if cached
    assert path in KnowledgeBaseService._cache
    cached_content = KnowledgeBaseService._cache[path]
    assert cached_content == content

    # 3. Modify cache manually to prove subsequent calls hit cache and not disk
    KnowledgeBaseService._cache[path] = "MOCK_CACHED_CONTENT"
    retrieved = await KnowledgeBaseService.get_lesson_content(path)
    assert retrieved == "MOCK_CACHED_CONTENT"

    # Clean cache again
    KnowledgeBaseService.clear_cache()


@pytest.mark.asyncio
async def test_missing_file_raises_404():
    """
    Verifies that requesting a file that does not exist raises a clean
    HTTP 404 exception.
    """
    with pytest.raises(HTTPException) as exc_info:
        await KnowledgeBaseService.get_lesson_content("phase-9/non_existent.md")
    assert exc_info.value.status_code == 404
    assert "was not found on the server" in exc_info.value.detail


@pytest.mark.asyncio
async def test_directory_traversal_protection():
    """
    Verifies that any request attempting to escape the curriculum root folder
    (e.g., using '../../') is blocked and raises an HTTP 404 exception.
    """
    traversal_path = "../../Backend/app/core/config.py"
    with pytest.raises(HTTPException) as exc_info:
        await KnowledgeBaseService.get_lesson_content(traversal_path)
    assert exc_info.value.status_code == 404
    # Traversal logs it, returning a generic not found message to clients
    assert "could not be found" in exc_info.value.detail
