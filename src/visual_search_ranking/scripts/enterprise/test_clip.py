"""
CLIP Model Testing Script

Verifies that the CLIP service is working correctly.
"""

import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent.parent.parent


def test_clip():
    """Test CLIP model loading and basic functionality."""
    # Add src to path for imports
    project_root = get_project_root()
    sys.path.insert(0, str(project_root / "src"))

    print('Loading CLIP service...')

    from visual_search_ranking.enterprise.clip_service import get_clip_service

    service = get_clip_service()
    print(f'Model loaded successfully!')
    print(f'Device: {service.device}')
    print(f'Embedding dim: {service.embedding_dim}')

    # Test text encoding
    print('\nTesting text encoding...')
    embedding = service.encode_text("red leather handbag")
    print(f'Text embedding shape: {embedding.shape}')
    print(f'Embedding norm: {sum(embedding**2)**0.5:.4f}')

    print('\nCLIP service test passed!')


if __name__ == "__main__":
    test_clip()
