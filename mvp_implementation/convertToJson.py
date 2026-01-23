import os
import json
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from tqdm import tqdm  # Import tqdm for the progress bar

# Set device to CUDA if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the pre-trained ResNet-50 model using the updated weights parameter and move it to the selected device
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model = torch.nn.Sequential(*(list(model.children())[:-1]))
model = model.to(device)
model.eval()

# Define image transformations
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),  # Consider alternatives if you need to preserve more details
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                         std=[0.229, 0.224, 0.225]),
])

# Define the base directory where your images are located
base_dir = '../images' 

# List to hold product records
data = []

# Traverse through each category folder (e.g., abstract, animal-painting, etc.)
categories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

# Initialize tqdm progress bar
with tqdm(total=sum([len(files) for r, d, files in os.walk(base_dir)]), desc="Processing images") as pbar:
    for category in categories:
        category_path = os.path.join(base_dir, category)
        for filename in os.listdir(category_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(category_path, filename)
                try:
                    # Load and preprocess the image
                    img = Image.open(file_path).convert("RGB")
                    input_tensor = preprocess(img)
                    input_batch = input_tensor.unsqueeze(0).to(device)  # Move to CUDA if available

                    # Extract embedding
                    with torch.no_grad():
                        embedding_tensor = model(input_batch)
                        # Flatten the embedding and move to CPU, then convert to list
                        embedding = embedding_tensor.flatten().cpu().tolist()
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue

                # Create a record for the product
                record = {
                    "product_id": f"{category}_{filename.split('.')[0]}",
                    "product_name": filename.split('.')[0],
                    "category": category,
                    "image_path": os.path.join(category, filename),
                    "embedding": embedding
                }
                data.append(record)
            pbar.update(1)  # Update progress bar after processing each image

# Write the dataset with embeddings to a JSON file
with open('../data/mvp/dataset_with_embeddings.json', 'w') as f:
    json.dump(data, f, indent=4)

print("JSON with embeddings created with", len(data), "entries.")
