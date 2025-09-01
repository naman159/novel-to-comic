# Model Usage Guide

## Overview

The Novel to Comic Generator uses different Gemini 2.5 Flash models for different tasks to optimize performance and capabilities.

## Model Selection

### Text Generation Tasks

For all text-based tasks (entity extraction, scene segmentation, panel planning), we use:

- **Model**: `gemini-2.5-flash`
- **Reason**: Optimized for text generation with fast response times
- **Use Cases**:
  - Extracting characters and locations from chapter text
  - Breaking chapters into logical scenes
  - Creating panel descriptions and composition prompts

### Image Generation Tasks

For all image generation tasks, we use:

- **Model**: `gemini-2.5-flash-image-preview`
- **Reason**: Specifically designed for image generation with enhanced visual capabilities
- **Use Cases**:
  - Generating character portraits
  - Creating location backgrounds
  - Composing final comic panels

## Implementation Details

### Text Generation

```python
response = client.generate_content(
    prompt,
    model="gemini-2.5-flash"
)
```

### Image Generation

```python
response = client.generate_content(
    prompt,
    model="gemini-2.5-flash-image-preview",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
    }
)
```

## Why This Matters

### Performance

- **Text Tasks**: `gemini-2.5-flash` is faster for text generation
- **Image Tasks**: `gemini-2.5-flash-image-preview` is optimized for image generation

### Quality

- **Text Tasks**: Better text understanding and generation
- **Image Tasks**: Enhanced image composition and visual consistency

### Cost Efficiency

- Using the right model for each task optimizes API usage
- Prevents unnecessary use of image generation capabilities for text tasks

## Task Breakdown

| Task               | Model                            | Purpose                           |
| ------------------ | -------------------------------- | --------------------------------- |
| Entity Extraction  | `gemini-2.5-flash`               | Identify characters and locations |
| Scene Segmentation | `gemini-2.5-flash`               | Break chapter into scenes         |
| Panel Planning     | `gemini-2.5-flash`               | Create panel descriptions         |
| Character Images   | `gemini-2.5-flash-image-preview` | Generate character portraits      |
| Location Images    | `gemini-2.5-flash-image-preview` | Generate location backgrounds     |
| Panel Composition  | `gemini-2.5-flash-image-preview` | Create final comic panels         |

## Benefits

1. **Optimized Performance**: Each task uses the most appropriate model
2. **Better Quality**: Specialized models for specialized tasks
3. **Cost Effective**: Efficient use of API resources
4. **Consistency**: Reliable results across different task types

## Future Considerations

As Gemini models evolve, we can easily update the model selection:

- Monitor for new specialized models
- Test performance improvements
- Update model selection based on results
- Consider model-specific optimizations
