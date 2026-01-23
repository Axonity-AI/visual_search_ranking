"""
CLIP Service

Handles CLIP model loading and embedding generation.
"""

import torch
import numpy as np
from PIL import Image
from typing import List, Union, Optional
from pathlib import Path
from transformers import CLIPProcessor, CLIPModel
import logging


class CLIPService:
    """Service for generating CLIP embeddings from images and text."""

    def __init__(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        device: Optional[str] = None
    ):
        """
        Initialize CLIP service.

        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name

        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.logger.info(f"Initializing CLIP model: {model_name}")
        self.logger.info(f"Using device: {self.device}")

        # Load model and processor
        try:
            self.model = CLIPModel.from_pretrained(model_name)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model = self.model.to(self.device)
            self.model.eval()

            # Get embedding dimension
            self.embedding_dim = self.model.config.projection_dim

            self.logger.info(f"CLIP model loaded successfully")
            self.logger.info(f"Embedding dimension: {self.embedding_dim}")

        except Exception as e:
            self.logger.error(f"Failed to load CLIP model: {e}")
            raise

    def encode_image(
        self,
        image: Union[Image.Image, str, Path],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for a single image.

        Args:
            image: PIL Image, image path, or path string
            normalize: Whether to L2-normalize the embedding

        Returns:
            numpy array of shape (embedding_dim,)
        """
        # Load image if path provided
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be PIL Image or path")

        # Process image
        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embedding
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)

        # Convert to numpy
        embedding = image_features.cpu().numpy().flatten()

        # Normalize if requested
        if normalize:
            embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def encode_images_batch(
        self,
        images: List[Union[Image.Image, str, Path]],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for multiple images in batches.

        Args:
            images: List of PIL Images or image paths
            batch_size: Number of images to process at once
            normalize: Whether to L2-normalize embeddings
            show_progress: Whether to print progress

        Returns:
            numpy array of shape (num_images, embedding_dim)
        """
        embeddings = []
        num_batches = (len(images) + batch_size - 1) // batch_size

        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]

            # Load images if paths provided
            loaded_batch = []
            for img in batch:
                if isinstance(img, (str, Path)):
                    loaded_batch.append(Image.open(img).convert('RGB'))
                else:
                    loaded_batch.append(img)

            # Process batch
            inputs = self.processor(
                images=loaded_batch,
                return_tensors="pt"
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate embeddings
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)

            # Convert to numpy
            batch_embeddings = image_features.cpu().numpy()

            # Normalize if requested
            if normalize:
                norms = np.linalg.norm(batch_embeddings, axis=1, keepdims=True)
                batch_embeddings = batch_embeddings / norms

            embeddings.append(batch_embeddings)

            if show_progress:
                batch_num = (i // batch_size) + 1
                print(f"Processed batch {batch_num}/{num_batches} "
                      f"({len(loaded_batch)} images)")

        return np.vstack(embeddings)

    def encode_text(
        self,
        text: Union[str, List[str]],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for text.

        Args:
            text: Text string or list of text strings
            normalize: Whether to L2-normalize embeddings

        Returns:
            numpy array of shape (embedding_dim,) for single text
            or (num_texts, embedding_dim) for multiple texts
        """
        is_single = isinstance(text, str)
        if is_single:
            text = [text]

        # Process text
        inputs = self.processor(
            text=text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embeddings
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)

        # Convert to numpy
        embeddings = text_features.cpu().numpy()

        # Normalize if requested
        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms

        return embeddings[0] if is_single else embeddings

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity score (0-1)
        """
        # Ensure embeddings are normalized
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    def compute_similarities(
        self,
        query_embedding: np.ndarray,
        database_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarities between query and database embeddings.

        Args:
            query_embedding: Query embedding of shape (embedding_dim,)
            database_embeddings: Database embeddings of shape (num_items, embedding_dim)

        Returns:
            numpy array of similarity scores of shape (num_items,)
        """
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)

        db_norms = np.linalg.norm(database_embeddings, axis=1, keepdims=True)
        db_norms[db_norms == 0] = 1  # Avoid division by zero
        database_norm = database_embeddings / db_norms

        # Compute dot products
        similarities = np.dot(database_norm, query_norm)

        return similarities

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "embedding_dim": self.embedding_dim
        }

    def __repr__(self):
        return (
            f"CLIPService(model={self.model_name}, "
            f"device={self.device}, "
            f"embedding_dim={self.embedding_dim})"
        )


# Singleton instance for shared use
_clip_service_instance = None


def get_clip_service(
    model_name: str = "openai/clip-vit-base-patch32",
    device: Optional[str] = None
) -> CLIPService:
    """
    Get or create CLIP service singleton instance.

    Args:
        model_name: HuggingFace model identifier
        device: Device to use ('cuda', 'cpu', or None for auto-detect)

    Returns:
        CLIPService instance
    """
    global _clip_service_instance

    if _clip_service_instance is None:
        _clip_service_instance = CLIPService(
            model_name=model_name,
            device=device
        )

    return _clip_service_instance
