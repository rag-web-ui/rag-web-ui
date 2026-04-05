# HuggingFace Embeddings Support

This document explains how to use HuggingFace embedding models with RAG Web UI.

## Configuration

Add the following to your `.env` file:

```bash
# Set embeddings provider to huggingface
EMBEDDINGS_PROVIDER=huggingface

# Optional: HuggingFace API token (only needed for gated models or API usage)
HUGGINGFACE_API_KEY=your_huggingface_token_here

# HuggingFace embedding model to use
HUGGINGFACE_EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Recommended Models

### Lightweight & Fast
- `sentence-transformers/all-MiniLM-L6-v2` (default)
  - Dimensions: 384
  - Best for: Quick prototyping, resource-constrained environments

### Balanced Performance
- `sentence-transformers/all-mpnet-base-v2`
  - Dimensions: 768
  - Best for: General purpose, good quality-speed tradeoff

- `BAAI/bge-small-en-v1.5`
  - Dimensions: 384
  - Best for: English text, good performance

### High Quality
- `BAAI/bge-large-en-v1.5`
  - Dimensions: 1024
  - Best for: When quality is priority over speed

- `BAAI/bge-base-en-v1.5`
  - Dimensions: 768
  - Best for: English text, high quality

### Multilingual
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  - Dimensions: 384
  - Best for: Multiple languages support

## Usage Notes

1. **First Run**: The model will be downloaded automatically on first use. This may take some time depending on model size.

2. **Model Storage**: Models are cached locally in `~/.cache/huggingface/` by default.

3. **API Token**: Only required for:
   - Gated models (models that require approval)
   - Using HuggingFace Inference API instead of local models

4. **Memory Requirements**: Larger models require more RAM. Ensure your system has sufficient memory.

5. **GPU Support**: If you have a GPU, the models will automatically use it for faster inference.

## Example Configuration

### Local Model (No API Key Needed)
```bash
EMBEDDINGS_PROVIDER=huggingface
HUGGINGFACE_EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### With API Token (For Gated Models)
```bash
EMBEDDINGS_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_EMBEDDINGS_MODEL=some-gated-model
```

## Troubleshooting

### Model Download Issues
If you encounter download issues, try:
1. Check your internet connection
2. Verify the model name is correct
3. For gated models, ensure you have access and provided a valid API token

### Memory Issues
If you run out of memory:
1. Use a smaller model (e.g., `all-MiniLM-L6-v2`)
2. Reduce batch size in processing
3. Increase system RAM or use a machine with more memory

### Performance Issues
To improve performance:
1. Use GPU if available
2. Choose a smaller model for faster inference
3. Consider using quantized models for production
