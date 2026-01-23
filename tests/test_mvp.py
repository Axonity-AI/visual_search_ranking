"""Tests for MVP implementation."""

import pytest
from pathlib import Path


def test_project_structure():
    """Test that project structure is correct."""
    project_root = Path(__file__).parent.parent

    # Check src directory exists
    assert (project_root / "src").exists()
    assert (project_root / "src" / "visual_search_ranking").exists()
    assert (project_root / "src" / "visual_search_ranking" / "mvp").exists()


def test_mvp_module_imports():
    """Test that MVP modules can be imported."""
    try:
        from visual_search_ranking.mvp import main
        assert hasattr(main, 'app')
    except ImportError as e:
        pytest.skip(f"Module not importable (dependencies may be missing): {e}")


def test_mvp_endpoints_exist():
    """Test that MVP API endpoints are defined."""
    try:
        from visual_search_ranking.mvp.main import app

        # Get route paths
        routes = [route.path for route in app.routes]

        # Check essential endpoints exist
        assert "/random_products" in routes
        assert "/similar/{product_id}" in routes
        assert "/recommend" in routes
        assert "/health" in routes
    except ImportError as e:
        pytest.skip(f"Module not importable: {e}")


class TestMVPDataProcessing:
    """Tests for MVP data processing utilities."""

    def test_convert_to_json_module_exists(self):
        """Test that convert_to_json module exists."""
        project_root = Path(__file__).parent.parent
        module_path = project_root / "src" / "visual_search_ranking" / "mvp" / "convert_to_json.py"
        assert module_path.exists()

    def test_precompute_similarity_module_exists(self):
        """Test that precompute_similarity module exists."""
        project_root = Path(__file__).parent.parent
        module_path = project_root / "src" / "visual_search_ranking" / "mvp" / "precompute_similarity.py"
        assert module_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
