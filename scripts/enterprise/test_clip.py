import sys
sys.path.insert(0, 'backend')

print('Loading CLIP service...')
from app.clip_service import get_clip_service

service = get_clip_service()
print(f'Model loaded successfully!')
print(f'Device: {service.device}')
print(f'Embedding dim: {service.embedding_dim}')
