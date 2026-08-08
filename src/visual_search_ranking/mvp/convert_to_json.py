"""
Image Embedding Generation Script.

Processes artwork images using ResNet-50 to create visual embeddings.
"""

import json
import os
from pathlib import Path

import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from tqdm import tqdm


def get_project_root() -> Path:
    """Get the project root directory."""
    # src/visual_search_ranking/mvp/convert_to_json.py -> 4 parents to repo root
    return Path(__file__).parent.parent.parent.parent


def generate_embeddings(
    images_dir: Path = None,
    output_path: Path = None,
    device: str = None
):
    """
    Generate ResNet-50 embeddings for all images.

    Args:
        images_dir: Directory containing image category folders
        output_path: Path for output JSON file
        device: Device to use ('cuda' or 'cpu', auto-detected if None)
    """
    project_root = get_project_root()

    if images_dir is None:
        images_dir = project_root / "images"
    if output_path is None:
        output_path = project_root / "data" / "mvp" / "dataset_with_embeddings.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Set device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device)
    print(f"Using device: {device}")

    # Load pre-trained ResNet-50 model
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model = torch.nn.Sequential(*(list(model.children())[:-1]))
    model = model.to(device)
    model.eval()

    # Define image transformations
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])

    # Collect all image files
    data = []
    categories = [d for d in os.listdir(images_dir) if (images_dir / d).is_dir()]

    total_files = sum(
        len([f for f in os.listdir(images_dir / cat)
             if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        for cat in categories
    )

    print(f"Processing {total_files} images across {len(categories)} categories...")

    with tqdm(total=total_files, desc="Processing images") as pbar:
        for category in categories:
            category_path = images_dir / category
            for filename in os.listdir(category_path):
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue

                file_path = category_path / filename
                try:
                    # Load and preprocess the image
                    img = Image.open(file_path).convert("RGB")
                    input_tensor = preprocess(img)
                    input_batch = input_tensor.unsqueeze(0).to(device)

                    # Extract embedding
                    with torch.no_grad():
                        embedding_tensor = model(input_batch)
                        embedding = embedding_tensor.flatten().cpu().tolist()

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    pbar.update(1)
                    continue

                # Create product record
                record = {
                    "product_id": f"{category}_{filename.split('.')[0]}",
                    "product_name": filename.split('.')[0],
                    "category": category,
                    "image_path": f"{category}/{filename}",
                    "embedding": embedding
                }
                data.append(record)
                pbar.update(1)

    # Write dataset
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Created JSON with {len(data)} entries at {output_path}")
    return data


if __name__ == "__main__":
    generate_embeddings()
