"""Tests for MVP implementation."""

import sys
from pathlib import Path

import pytest

# Ensure src is in path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestProjectStructure:
    """Test project structure is correct."""

    def test_src_directory_exists(self):
        """Test that src directory exists."""
        assert (project_root / "src").exists()

    def test_package_directory_exists(self):
        """Test that visual_search_ranking package exists."""
        assert (project_root / "src" / "visual_search_ranking").exists()

    def test_mvp_directory_exists(self):
        """Test that MVP module exists."""
        assert (project_root / "src" / "visual_search_ranking" / "mvp").exists()

    def test_mvp_main_exists(self):
        """Test that MVP main.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "mvp" / "main.py").exists()

    def test_mvp_convert_to_json_exists(self):
        """Test that convert_to_json.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "mvp" / "convert_to_json.py").exists()

    def test_mvp_precompute_similarity_exists(self):
        """Test that precompute_similarity.py exists."""
        assert (project_root / "src" / "visual_search_ranking" / "mvp" / "precompute_similarity.py").exists()


class TestMVPImports:
    """Test MVP module imports."""

    def test_mvp_main_imports(self):
        """Test that MVP main module can be imported."""
        try:
            from visual_search_ranking.mvp import main
            assert hasattr(main, 'app')
        except ImportError as e:
            pytest.skip(f"Module not importable (missing dependencies): {e}")

    def test_mvp_convert_to_json_imports(self):
        """Test that convert_to_json module can be imported."""
        try:
            from visual_search_ranking.mvp import convert_to_json
            assert hasattr(convert_to_json, 'generate_embeddings')
        except ImportError as e:
            pytest.skip(f"Module not importable (missing dependencies): {e}")

    def test_mvp_precompute_similarity_imports(self):
        """Test that precompute_similarity module can be imported."""
        try:
            from visual_search_ranking.mvp import precompute_similarity
            assert hasattr(precompute_similarity, 'compute_similarities')
        except ImportError as e:
            pytest.skip(f"Module not importable (missing dependencies): {e}")


class TestMVPEndpoints:
    """Test MVP API endpoints."""

    def test_endpoints_exist(self):
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

    def test_health_endpoint_returns_dict(self):
        """Test health endpoint returns expected structure."""
        try:
            from visual_search_ranking.mvp.main import health_check

            result = health_check()
            assert isinstance(result, dict)
            assert "status" in result
            assert "data_loaded" in result
        except ImportError as e:
            pytest.skip(f"Module not importable: {e}")


class TestMVPUtilities:
    """Test MVP utility functions."""

    def test_get_project_root(self):
        """Test project root detection."""
        try:
            from visual_search_ranking.mvp.convert_to_json import get_project_root

            root = get_project_root()
            assert root.exists()
            # Should contain src directory
            assert (root / "src").exists()
        except ImportError as e:
            pytest.skip(f"Module not importable: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
