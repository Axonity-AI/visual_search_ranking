"""Tests for Enterprise implementation."""

import sys
from pathlib import Path

import pytest

# Ensure src is in path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestProjectStructure:
    """Test enterprise project structure is correct."""

    def test_enterprise_directory_exists(self):
        """Test that enterprise module exists."""
        assert (project_root / "src" / "visual_search_ranking" / "enterprise").exists()

    def test_enterprise_main_exists(self):
        """Test that enterprise main.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "enterprise" / "main.py").exists()

    def test_clip_service_exists(self):
        """Test that clip_service.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "enterprise" / "clip_service.py").exists()

    def test_vector_db_exists(self):
        """Test that vector_db.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "enterprise" / "vector_db.py").exists()


class TestEnterpriseImports:
    """Test enterprise module imports."""

    def test_vector_db_imports(self):
        """Test that vector_db module can be imported."""
        try:
            from visual_search_ranking.enterprise import vector_db
            assert hasattr(vector_db, 'get_vector_db')
            assert hasattr(vector_db, 'SearchResult')
            assert hasattr(vector_db, 'VectorDB')
        except ImportError as e:
            pytest.skip(f"Module not importable (missing dependencies): {e}")

    def test_clip_service_imports(self):
        """Test that clip_service module can be imported."""
        try:
            from visual_search_ranking.enterprise import clip_service
            assert hasattr(clip_service, 'CLIPService')
            assert hasattr(clip_service, 'get_clip_service')
        except ImportError as e:
            pytest.skip(f"Module not importable (missing dependencies): {e}")

    def test_enterprise_main_imports(self):
        """Test that enterprise main module can be imported."""
        try:
            from visual_search_ranking.enterprise import main
            assert hasattr(main, 'app')
        except ImportError as e:
            pytest.skip(f"Module not importable (missing dependencies): {e}")


class TestEnterpriseEndpoints:
    """Test enterprise API endpoints."""

    def test_endpoints_exist(self):
        """Test that enterprise API endpoints are defined."""
        try:
            from visual_search_ranking.enterprise.main import app

            # Get route paths
            routes = [route.path for route in app.routes]

            # Check essential endpoints exist
            assert "/health" in routes
            assert "/stats" in routes
            assert "/search" in routes
            assert "/search/text" in routes
            assert "/embed" in routes
        except ImportError as e:
            pytest.skip(f"Module not importable: {e}")


class TestVectorDBAbstraction:
    """Test vector database abstraction layer."""

    def test_search_result_dataclass(self):
        """Test SearchResult dataclass."""
        try:
            from visual_search_ranking.enterprise.vector_db import SearchResult

            result = SearchResult(
                id="test_id",
                score=0.95,
                metadata={"key": "value"}
            )
            assert result.id == "test_id"
            assert result.score == 0.95
            assert result.metadata == {"key": "value"}
        except ImportError as e:
            pytest.skip(f"Module not importable: {e}")

    def test_get_vector_db_invalid_type(self):
        """Test get_vector_db raises for invalid type."""
        try:
            from visual_search_ranking.enterprise.vector_db import get_vector_db

            with pytest.raises(ValueError):
                get_vector_db("invalid_type")
        except ImportError as e:
            pytest.skip(f"Module not importable: {e}")


class TestEnterpriseScripts:
    """Test enterprise utility scripts exist."""

    def test_index_vectors_exists(self):
        """Test that index_vectors.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "scripts" / "enterprise" / "index_vectors.py").exists()

    def test_organize_datasets_exists(self):
        """Test that organize_datasets.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "scripts" / "enterprise" / "organize_datasets.py").exists()

    def test_test_clip_exists(self):
        """Test that test_clip.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "scripts" / "enterprise" / "test_clip.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
