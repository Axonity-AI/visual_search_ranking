"""Tests for Enterprise implementation."""

import pytest
from pathlib import Path


def test_project_structure():
    """Test that project structure is correct."""
    project_root = Path(__file__).parent.parent

    # Check enterprise directory exists
    assert (project_root / "src" / "visual_search_ranking" / "enterprise").exists()


def test_enterprise_module_imports():
    """Test that enterprise modules can be imported."""
    try:
        from visual_search_ranking.enterprise import clip_service
        from visual_search_ranking.enterprise import vector_db

        assert hasattr(clip_service, 'CLIPService')
        assert hasattr(clip_service, 'get_clip_service')
        assert hasattr(vector_db, 'VectorDB')
        assert hasattr(vector_db, 'get_vector_db')
    except ImportError as e:
        pytest.skip(f"Module not importable (dependencies may be missing): {e}")


def test_enterprise_endpoints_exist():
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


class TestCLIPService:
    """Tests for CLIP service functionality."""

    def test_clip_service_module_exists(self):
        """Test that clip_service module exists."""
        project_root = Path(__file__).parent.parent
        module_path = project_root / "src" / "visual_search_ranking" / "enterprise" / "clip_service.py"
        assert module_path.exists()

    def test_vector_db_module_exists(self):
        """Test that vector_db module exists."""
        project_root = Path(__file__).parent.parent
        module_path = project_root / "src" / "visual_search_ranking" / "enterprise" / "vector_db.py"
        assert module_path.exists()


class TestEnterpriseScripts:
    """Tests for enterprise utility scripts."""

    def test_generate_embeddings_exists(self):
        """Test that generate_embeddings script exists."""
        project_root = Path(__file__).parent.parent
        script_path = project_root / "src" / "visual_search_ranking" / "scripts" / "enterprise" / "generate_embeddings.py"
        assert script_path.exists()

    def test_index_vectors_exists(self):
        """Test that index_vectors script exists."""
        project_root = Path(__file__).parent.parent
        script_path = project_root / "src" / "visual_search_ranking" / "scripts" / "enterprise" / "index_vectors.py"
        assert script_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
